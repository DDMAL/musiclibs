import scorched
import ujson as json
import requests

from misirlou.models.manifest import Manifest
from misirlou.helpers.IIIFImporter import WIPManifest
from django.conf import settings
import django.core.exceptions as django_exceptions


ERROR_MAPPING = {
    1: "No database entry with this pk.",
    2: "Could not resolve this pk in solr.",
    3: "Timeout retrieving remote_manifest.",
    4: "Failed to retrieve manifest.",
    5: "Manifest: stored remote url is not https.",
    6: "Manifest: SSL certificate verification failed.",
    7: "Local manifest hash DNE remote manifest contents.",
    8: "Indexed document has no thumbnail.",
    9: "Could not retrieve indexed thumbnail.",
    10: "Stored thumbnail is not IIIF."
}


class ManifestTesterException(Exception):
    pass


class ManifestTester:
    solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)

    # Modify these constants via kwargs to

    WARN_HTTPS_STORED = True  # Warn if stored url is not https.
    WARN_HTTPS_VERIFY = True  # Warn if https verification fails on remote.
    WARN_MISSING_THUMBNAIL = True  # Warn if there is no indexed thumbnail.
    WARN_NON_IIIF_THUMBNAIL = True  # Warn if thumbnail is not IIIF service.
    WARN_IRRETRIEVABLE_THUMBNAIL = True  # Warn if thumbnail can't be loaded.

    RAISE_MISSING_LOCAL = True  # Treat a missing local representation as invalid.
    RAISE_RETRIEVAL_TIMEOUT = True  # Treat timeout on remote as invalid.
    RAISE_RETRIEVAL_FAIL = True     # Treat retrieval fail of remote as invalid.
    RAISE_HASH_INEQUALITY = True    # Treat altered remote as invalid.

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
            import pdb
            pdb.set_trace()
            self._retrieve_stored_manifest()
            self._retrieve_remote_manifest()
            self._compare_manifest_hashes()
            self._retrieve_thumbnail()
            self._is_valid = True
        except ManifestTesterException as e:
            self.errors.append(e.args[0])
            self._is_valid = False

    def _retrieve_stored_manifest(self):
        """Retrieve the stored manifest from solr and postgres.

        The manifest stored in solr is stored in self.local_json.
        The minimal solr response for the manifest is stored in self.solr_resp.
        The record from postgres is stored in self.orm_object.
        """
        try:
            self.orm_object = Manifest.objects.get(pk=self.pk)
        except django_exceptions.ObjectDoesNotExist and self.RAISE_MISSING_LOCAL:
            raise ManifestTesterException((1, ERROR_MAPPING[1]))

        response = self.solr_conn.query(self.pk).set_requesthandler('/manifest').execute()
        if response.result.numFound != 1:
            raise ManifestTesterException((2, ERROR_MAPPING[2]))
        self.local_json = json.loads(response.result.docs[0]['manifest'])

        response = self.solr_conn.query(id=self.pk).set_requesthandler('/minimal').execute()
        if response.result.numFound != 1:
            raise ManifestTesterException((2, ERROR_MAPPING[2]))
        self.solr_resp = response.result.docs[0]

    def _retrieve_remote_manifest(self):
        """Test the ability to fetch this manifest from the remote.

        An SHA1 hash is computed and stored in self.remote_hash.
        The manifest at the location is stored as self.remote_json.
        """
        remote_url = self.local_json['@id']

        if not remote_url.startswith('https') and self.WARN_HTTPS_STORED:
            self.warnings.append((5, ERROR_MAPPING[5]))

        resp = None
        try:
            resp = requests.get(remote_url, timeout=20)
        except requests.exceptions.SSLError and self.WARN_HTTPS_VERIFY:
            self.warnings.append((6, ERROR_MAPPING[6]))
        if not resp:
            try:
                resp = requests.get(remote_url, verify=False, timeout=20)
            except requests.exceptions.Timeout and self.RAISE_RETRIEVAL_TIMEOUT:
                raise ManifestTesterException((3, ERROR_MAPPING[3]))

        if (resp.status_code < 200 or resp.status_code >= 400) and self.RAISE_RETRIEVAL_FAIL:
            raise ManifestTesterException((4, ERROR_MAPPING[4]))

        self.remote_hash = WIPManifest.generate_manifest_hash(resp.text)
        self.remote_json = json.loads(resp.text)

    def _compare_manifest_hashes(self):
        """Test that the stored hash is equal to the contents at the remote.

        If these are not equal, it indicates that we need to reindex the
        manifest to be up to date.
        """
        if self.orm_object.manifest_hash == self.remote_hash:
            return
        if self.RAISE_HASH_INEQUALITY:
            raise ManifestTesterException((7, ERROR_MAPPING[7]))
        else:
            self.warnings.append((7, ERROR_MAPPING[7]))

    def _retrieve_thumbnail(self):
        """Test that the thumbnail exists and can be retrieved."""
        thumbnail = self.solr_resp['thumbnail']
        if not thumbnail and self.WARN_MISSING_THUMBNAIL:
            self.warnings.append((8, ERROR_MAPPING[8]))

        try:
            thumbnail = json.loads(thumbnail)
            thumbnail_url = thumbnail['@id']
        except ValueError:
            if self.WARN_NON_IIIF_THUMBNAIL:
                self.warnings.append((10, ERROR_MAPPING[10]))
            thumbnail_url = thumbnail
        
        resp = requests.get(thumbnail_url, stream=True)
        if resp.status_code < 200 or resp.status_code >= 400 and\
                self.WARN_IRRETRIEVABLE_THUMBNAIL:
            self.warnings.append((9, ERROR_MAPPING[9]))




