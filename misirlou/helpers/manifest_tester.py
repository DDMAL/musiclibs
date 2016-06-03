""" Manage testing of manifests stored in musiclibs.

The ManifestTester class can be used to run a stored manifest through a
series of tests and return a set of errors and warnings. Errors should be
considered critical, and the manifest should be hidden until the error is
addressed. Warnings are non-critical issues that may effect the user experience
negatively.
"""
import scorched
import ujson as json
import requests

from misirlou.models.manifest import Manifest
from misirlou.helpers.IIIFImporter import WIPManifest
from django.conf import settings
import django.core.exceptions as django_exceptions

# Error code mappings.
NO_DB_RECORD = 1
SOLR_RECORD_ERROR = 2
TIMEOUT_REMOTE_RETRIEVAL = 3
FAILED_REMOTE_RETRIEVAL = 4
HTTPS_STORED = 5
MANIFEST_SSL_FAILURE = 6
HASH_MISMATCH = 7
NO_THUMBNAIL = 8
IRRETRIEVABLE_THUMBNAIL = 9
NON_IIIF_THUMBNAIL = 10

ERROR_MAPPING = {
    NO_DB_RECORD: "No database entry with this pk.",
    SOLR_RECORD_ERROR: "Could not resolve this pk in solr.",
    TIMEOUT_REMOTE_RETRIEVAL: "Timeout retrieving remote_manifest.",
    FAILED_REMOTE_RETRIEVAL: "Failed to retrieve manifest.",
    HTTPS_STORED: "Manifest: stored remote url is not https.",
    MANIFEST_SSL_FAILURE: "Manifest: SSL certificate verification failed.",
    HASH_MISMATCH: "Local manifest hash DNE remote manifest contents.",
    NO_THUMBNAIL: "Indexed document has no thumbnail.",
    IRRETRIEVABLE_THUMBNAIL: "Could not retrieve indexed thumbnail.",
    NON_IIIF_THUMBNAIL: "Stored thumbnail is not IIIF."
}


class ManifestTesterException(Exception):
    pass


class ManifestTester:
    """Run a stored manifest through a validation procedure."""
    solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)

    # Modify these constants via kwargs.
    WARN_HTTPS_STORED = True  # Warn if stored url is not https.
    WARN_MANIFEST_SSL_FAILURE = True  # Warn if https verification fails on remote.
    WARN_NO_THUMBNAIL = True  # Warn if there is no indexed thumbnail.
    WARN_NON_IIIF_THUMBNAIL = True  # Warn if thumbnail is not IIIF service.
    WARN_IRRETRIEVABLE_THUMBNAIL = True  # Warn if thumbnail can't be loaded.

    RAISE_TIMEOUT_REMOTE_RETRIEVAL = True  # Treat timeout on remote as invalid.
    RAISE_FAILED_REMOTE_RETRIEVAL = True     # Treat retrieval fail of remote as invalid.
    RAISE_HASH_MISMATCH = True    # Treat altered remote as invalid.

    def __init__(self, pk, **kwargs):
        self.pk = pk
        self.errors = []
        self.warnings = []
        self.local_json = None
        self.solr_resp = None
        self.remote_json = None
        self.remote_hash = None
        self.orm_object = None
        self._is_valid = None

        for k, v in kwargs.items():
            if (k.startswith('WARN') or k.startswith('RAISE')) and\
                    k in dir(self):
                self.__setattr__(k, v)

    @property
    def is_valid(self):
        if self._is_valid is None:
            self.validate()
        return self._is_valid

    def validate(self):
        try:
            self._retrieve_stored_manifest()
            self._retrieve_remote_manifest()
            self._compare_manifest_hashes()
            self._retrieve_thumbnail()
            self._is_valid = True
        except ManifestTesterException as e:
            self.errors.append(e.args[0])
            self._is_valid = False

    def get_error(self, index):
        """Return tuple with index and assosiated message."""
        return index, ERROR_MAPPING[index]

    def _retrieve_stored_manifest(self):
        """Retrieve the stored manifest from solr and postgres.

        The manifest stored in solr is stored in self.local_json.
        The minimal solr response for the manifest is stored in self.solr_resp.
        The record from postgres is stored in self.orm_object.
        """
        try:
            self.orm_object = Manifest.objects.get(pk=self.pk)
        except django_exceptions.ObjectDoesNotExist:
            raise ManifestTesterException(self.get_error(NO_DB_RECORD))

        response = self.solr_conn.query(self.pk).set_requesthandler('/manifest').execute()
        if response.result.numFound != 1:
            raise ManifestTesterException(self.get_error(SOLR_RECORD_ERROR))
        self.local_json = json.loads(response.result.docs[0]['manifest'])

        response = self.solr_conn.query(id=self.pk).set_requesthandler('/minimal').execute()
        if response.result.numFound != 1:
            raise ManifestTesterException(self.get_error(SOLR_RECORD_ERROR))
        self.solr_resp = response.result.docs[0]

    def _retrieve_remote_manifest(self):
        """Test the ability to fetch this manifest from the remote.

        An SHA1 hash is computed and stored in self.remote_hash.
        The manifest at the location is stored as self.remote_json.
        """
        remote_url = self.local_json['@id']

        if not remote_url.startswith('https') and self.WARN_HTTPS_STORED:
            self.warnings.append(self.get_error(HTTPS_STORED))

        resp = None
        try:
            resp = requests.get(remote_url, timeout=20)
        except requests.exceptions.SSLError and self.WARN_MANIFEST_SSL_FAILURE:
            self.warnings.append(self.get_error(MANIFEST_SSL_FAILURE))
        if not resp:
            try:
                resp = requests.get(remote_url, verify=False, timeout=20)
            except requests.exceptions.Timeout and self.RAISE_TIMEOUT_REMOTE_RETRIEVAL:
                raise ManifestTesterException(self.get_error(TIMEOUT_REMOTE_RETRIEVAL))

        if (resp.status_code < 200 or resp.status_code >= 400) and self.RAISE_FAILED_REMOTE_RETRIEVAL:
            raise ManifestTesterException(self.get_error(FAILED_REMOTE_RETRIEVAL))

        self.remote_hash = WIPManifest.generate_manifest_hash(resp.text)
        self.remote_json = json.loads(resp.text)

    def _compare_manifest_hashes(self):
        """Test that the stored hash is equal to the contents at the remote.

        If these are not equal, it indicates that we need to reindex the
        manifest to be up to date.
        """
        if self.orm_object.manifest_hash == self.remote_hash:
            return
        if self.RAISE_HASH_MISMATCH:
            raise ManifestTesterException(self.get_error(HASH_MISMATCH))
        else:
            self.warnings.append(self.get_error(HASH_MISMATCH))

    def _retrieve_thumbnail(self):
        """Test that the thumbnail exists and can be retrieved."""
        thumbnail = self.solr_resp['thumbnail']
        if not thumbnail and self.WARN_NO_THUMBNAIL:
            self.warnings.append(self.get_error(NO_THUMBNAIL))

        try:
            thumbnail = json.loads(thumbnail)
            thumbnail_url = thumbnail['@id']
        except ValueError:
            if self.WARN_NON_IIIF_THUMBNAIL:
                self.warnings.append(self.get_error(NON_IIIF_THUMBNAIL))
            thumbnail_url = thumbnail

        try:
            resp = requests.get(thumbnail_url, stream=True)
        except requests.exceptions.Timeout:
            if self.WARN_IRRETRIEVABLE_THUMBNAIL:
                self.warnings.append(self.get_error(IRRETRIEVABLE_THUMBNAIL))
        else:
            if resp.status_code < 200 or resp.status_code >= 400 and\
                    self.WARN_IRRETRIEVABLE_THUMBNAIL:
                self.warnings.append(self.get_error(IRRETRIEVABLE_THUMBNAIL))




