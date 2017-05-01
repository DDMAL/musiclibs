"""
Manage testing of manifests stored in musiclibs.

The ManifestTester class can be used to run a stored manifest through a
series of tests and return a set of errors and warnings. Errors should be
considered critical, and the manifest should be hidden until the error is
addressed. Warnings are non-critical issues that may effect the user experience
negatively.
"""
import scorched
import ujson as json
import requests
import uuid
import random

from django.conf import settings
import django.core.exceptions as django_exceptions
from django.utils import timezone

import misirlou.models as models
from misirlou.helpers.manifest_utils.importer import ManifestImporter
from misirlou.helpers.manifest_utils.errors import ErrorMap
from misirlou.helpers.requester import DEFAULT_REQUESTER


class ManifestTesterException(Exception):
    pass

requester = DEFAULT_REQUESTER


class ManifestTester:
    """Run a stored manifest through a validation procedure."""

    # Errors are defined in misirlou.helpers.manifest_errors
    _error_map = ErrorMap()

    # Modify these constants via kwargs to set error handling.
    WARN_HTTPS_STORED = True  # Warn if stored url is not https.
    WARN_MANIFEST_SSL_FAILURE = True  # Warn if https verification fails on remote.
    WARN_NO_THUMBNAIL = True  # Warn if there is no indexed thumbnail.
    WARN_NON_IIIF_THUMBNAIL = True  # Warn if thumbnail is not IIIF service.
    WARN_IRRETRIEVABLE_THUMBNAIL = True  # Warn if thumbnail can't be loaded.
    WARN_HASH_MISMATCH = False
    WARN_NON_IIIF_IMAGE_IN_SEQUENCE = True

    RAISE_NO_DB_RECORD = True  # Treat inability to find DB record as invalid.
    RAISE_SOLR_RECORD_ERROR = True  # Treat inability to find solr doc as invalid.
    RAISE_TIMEOUT_REMOTE_RETRIEVAL = True  # Treat timeout on remote as invalid.
    RAISE_FAILED_REMOTE_RETRIEVAL = True     # Treat retrieval fail of remote as invalid.
    RAISE_HASH_MISMATCH = True    # Treat altered remote as invalid.
    RAISE_FAILED_IMAGE_REQUEST = True
    RAISE_NON_IIIF_IMAGE_IN_SEQUENCE = False

    def __init__(self, pk, **kwargs):
        if isinstance(pk, uuid.UUID):
            pk = str(pk)
        self.pk = pk
        self.warnings = []
        self.error = None
        self.local_json = None
        self.solr_resp = None
        self.remote_json = None
        self.remote_hash = None
        self.orm_object = None
        self._is_valid = None
        self._solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)

        for k, v in kwargs.items():
            if (k.startswith('WARN') or k.startswith('RAISE')) and\
                    k in dir(self):
                self.__setattr__(k, v)

    @property
    def is_valid(self):
        if self._is_valid is None:
            self.validate()
        return self._is_valid

    def validate(self, save_result=False, test_remote=True):
        try:
            self._retrieve_stored_manifest()
            if test_remote:
                self._retrieve_remote_manifest()
                self._compare_manifest_hashes()
            self._retrieve_thumbnail()
            self._retrieve_some_image()
            self._is_valid = True
        except ManifestTesterException as e:
            self.error = (e.args[0])
            self._is_valid = False
        finally:
            if save_result:
                self.save_result()

    def save_result(self):
        self.is_valid
        if not self.orm_object:
            raise RuntimeError("Could not find DB row to save results.")
        self.orm_object.error = self.error if self.error else 0
        self.orm_object.warnings = self.warnings
        self.orm_object.last_tested = timezone.now()
        self.orm_object.is_valid = self._is_valid
        self.orm_object.save()
        self.orm_object._update_solr_validation()

    def _handle_err(self, err):
        """Either raise an error or append a warning based on settings."""
        if isinstance(err, int):
            err = self._error_map[err]
        try:
            should_raise = self.__getattribute__("RAISE_"+err)
        except AttributeError:
            pass
        else:
            if should_raise:
                raise ManifestTesterException(self._error_map[err])

        try:
            should_warn = self.__getattribute__("WARN_"+err)
        except AttributeError:
            pass
        else:
            if should_warn:
                self.warnings.append(self._error_map[err])

    def _retrieve_stored_manifest(self):
        """Retrieve the stored manifest from solr and postgres.

        The manifest stored in solr is stored in self.local_json.
        The minimal solr response for the manifest is stored in self.solr_resp.
        The record from postgres is stored in self.orm_object.
        """
        try:
            self.orm_object = models.Manifest.objects.get(pk=self.pk)
        except django_exceptions.ObjectDoesNotExist:
            self._handle_err("NO_DB_RECORD")

        response = self._solr_conn.query(self.pk).set_requesthandler('/manifest').execute()
        if response.result.numFound != 1:
            self._handle_err("SOLR_RECORD_ERROR")
        self.local_json = json.loads(response.result.docs[0]['manifest'])

        response = self._solr_conn.query(id=self.pk).set_requesthandler('/minimal').execute()
        if response.result.numFound != 1:
            self._handle_err("SOLR_RECORD_ERROR")
        self.solr_resp = response.result.docs[0]

    def _retrieve_remote_manifest(self):
        """Test the ability to fetch this manifest from the remote.

        An SHA1 hash is computed and stored in self.remote_hash.
        The manifest at the location is stored as self.remote_json.
        """
        remote_url = self.local_json['@id']

        if not remote_url.startswith('https'):
            self._handle_err("HTTPS_STORED")

        resp = None
        try:
            resp = requester.get(remote_url, timeout=20)
        except requests.exceptions.SSLError:
            self._handle_err("MANIFEST_SSL_FAILURE")
        if not resp:
            try:
                resp = requester.get(remote_url, verify=False, timeout=20)
            except requests.exceptions.Timeout:
                self._handle_err("TIMEOUT_REMOTE_RETRIEVAL")

        if (resp.status_code < 200 or resp.status_code >= 400) and self.RAISE_FAILED_REMOTE_RETRIEVAL:
            self._handle_err("FAILED_REMOTE_RETRIEVAL")

        self.remote_hash = ManifestImporter.generate_manifest_hash(resp.text)
        self.remote_json = json.loads(resp.text)

    def _compare_manifest_hashes(self):
        """Test that the stored hash is equal to the contents at the remote.

        If these are not equal, it indicates that we need to reindex the
        manifest to be up to date.
        """
        if self.orm_object.manifest_hash == self.remote_hash:
            return
        self._handle_err("HASH_MISMATCH")

    def _retrieve_thumbnail(self):
        """Test that the thumbnail exists and can be retrieved."""
        thumbnail = self.solr_resp.get('thumbnail')
        if not thumbnail:
            self._handle_err("NO_THUMBNAIL")
            return
        try:
            thumbnail = json.loads(thumbnail)
        except ValueError:
            self._handle_err("NON_IIIF_THUMBNAIL")
            return
        try:
            thumbnail_url = thumbnail['@id']
        except TypeError:
            thumbnail_url = thumbnail

        try:
            if self._is_IIIF_image_resource(thumbnail):
                resp = self._get_small_IIIF_image(thumbnail)
            else:
                resp = requester.get(thumbnail_url, stream=True)
        except requests.exceptions.Timeout:
            self._handle_err("IRRETRIEVABLE_THUMBNAIL")
        else:
            if resp.status_code < 200 or resp.status_code >= 400:
                self._handle_err("IRRETRIEVABLE_THUMBNAIL")

    def _retrieve_some_image(self):
        """Test that we can retrieve some image from the IIIF image service."""
        seq = self.local_json.get('sequences', [None])
        seq = seq[0]
        if not seq:
            self._handle_err("FAILED_IMAGE_REQUEST")
            return
        canvases = seq['canvases']
        rand_index = random.randint(0, len(canvases)-1)
        canvas = canvases[rand_index]
        image = canvas['images'][0]
        resource = image['resource']
        if not self._is_IIIF_image_resource(resource):
            self._handle_err("NON_IIIF_IMAGE_IN_SEQUENCE")
        try:
            resp = self._get_small_IIIF_image(resource)
        except requests.exceptions.Timeout:
            self._handle_err("FAILED_IMAGE_REQUEST")
        else:
            if resp.status_code < 200 or resp.status_code >= 400:
                self._handle_err("FAILED_IMAGE_REQUEST")

    def _is_IIIF_image_resource(self, resource):
        """Helper function determines if dict is IIIF image resource."""
        if not isinstance(resource, dict):
            return False
        service = resource.get('service')
        if not service or not isinstance(service, dict):
            return False
        return service.get('@context') == "http://iiif.io/api/image/2/context.json"

    def _get_small_IIIF_image(self, resource):
        """Helper function makes request for scaled down image."""
        uri = resource['@id']
        uri = uri.replace("/full/full/", "/full/100,/")
        return requester.get(uri)


