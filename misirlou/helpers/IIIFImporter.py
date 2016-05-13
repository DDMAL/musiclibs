import ujson as json
import scorched
import requests
import hashlib

from urllib import parse
from django.conf import settings
from django.utils import timezone
from misirlou.models.manifest import Manifest
from misirlou.helpers.IIIFSchema import ManifestValidator

indexed_langs = ["en", "fr", "it", "de"]
timeout_error = "Timed out fetching '{}'"

def get_doc(remote_url):
    """Defaults for getitng a document using requests."""
    return requests.get(remote_url, verify=False, timeout=20)

class ManifestImportError(Exception):
    pass


class ManifestPreImporter:
    """Get document ready for import by parsing basic data.

    Fetches the document and makes sure it has some basic properties.

    get_all_urls(self) will recurse into all nested collections and
    compile a list of manifest urls to be imported.
    """
    def __init__(self, remote_url):
        self.remote_url = remote_url
        self.errors = []
        self.warnings = []
        self.json = {}
        self.type = ""
        self._prepare_for_creation()

    def _prepare_for_creation(self):
        try:
            manifest_resp = get_doc(self.remote_url)
        except requests.exceptions.Timeout:
            self.errors.append(timeout_error.format(self.remote_url))
            return
        manifest_data = manifest_resp.text

        try:
            self.json = json.loads(manifest_data)
        except ValueError:
            self.errors.append("Retrieved document is not valid JSON.")
            return

        self.type = self.json.get('@type')
        if not self.type:
            self.errors.append("Parsed document has no @type.")
            return

        doc_id = self.json.get("@id")
        if not doc_id:
            if self.type == "sc:Collection":
                self.warnings.append("Collection has no @id value.")
            if self.type == "sc:Manifest":
                self.errors.append("Manifest has no @id value.")
                return

    def get_all_urls(self):
        """Get all the importable URLs related to the remote_url.

        :return: List of strings with importable URLs.
        """
        if len(self.errors):
            return []

        if self.type == "sc:Manifest":
            return [self.remote_url]

        elif self.type == "sc:Collection":
            return self._get_nested_manifests(self.json)

    def _get_nested_manifests(self, json_obj, manifest_set=None):
        """Find and add nested manifest urls to manifest_set.

        :param json_obj: A json decoded Manifest or Collection.
        :param manifest_set: A set for collecting remote_urls.
        :return: A list of urls of manifests.
        """

        if manifest_set is None:
            manifest_set = set()

        # Recurse into members key.
        members = json_obj.get('members', [])
        for member in members:
            if member['@type'] == 'sc:Manifest':
                manifest_set.add(member['@id'])
            if member['@type'] == 'sc:Collection:':
                self._get_nested_manifests(member, manifest_set)

        # Handle an embedded list of manifests.
        manifests = json_obj.get('manifests', [])
        for man in manifests:
            tmp_url = man.get("@id")
            if(tmp_url):
                manifest_set.add(tmp_url)

        collections = json_obj.get('collections', [])
        for col in collections:
            # Handle embedded collections.
            manifests = col.get('manifests')
            if manifests:
                self._get_nested_manifests(col, manifest_set)
                continue

            # Handle linked collections.
            col_url = col.get("@id")
            if not col_url:
                continue
            try:
                col_resp = get_doc(col_url)
            except requests.exceptions.Timeout:
                self.errors.append("Timed out fetching nested collection at '{}'".format(col_url))
                continue

            col_data = col_resp.text
            col_json = json.loads(col_data)
            self._get_nested_manifests(col_json, manifest_set)

        return list(manifest_set)


class WIPManifest:
    # A class for manifests that are being built
    def __init__(self, remote_url, shared_id, prefetched_data=None):
        """Create a WIPManifest

        :param remote_url: URL of IIIF manifest.
        :param shared_id: ID to apply as the manifest's uuid.
        :param prefetched_data: Dict of manifest at remote_url.
        :return:
        """
        self.remote_url = remote_url
        self.id = shared_id
        self.doc = {}  # for solr_indexing
        self.errors = []
        self.warnings = []
        self.in_db = False
        self.db_rep = None
        self.manifest_hash = None
        if prefetched_data:
            self._generate_manifest_hash(prefetched_data)
            self.json = json.loads(prefetched_data)
        else:
            self.json = {}

    def create(self):
        """ Go through the steps of validating and indexing this manifest.
        Return False if error hit, True otherwise."""

        try:
            self._retrieve_json()  # Get the doc if we don't have it.
        except ManifestImportError:
            return False
        if self._check_db_duplicates():  # Check if this doc is in DB.
            return True

        try:
            self.__validate()
        except ManifestImportError:
            return False

        self._create_db_entry()
        self._solr_index()
        return True

    def __validate(self):
        """Validate for proper IIIF API formatting"""
        v = ManifestValidator()
        v.validate(self.json)
        if v.is_valid:
            return
        else:
            self.errors.append(v.errors)
            raise ManifestImportError

    def _retrieve_json(self, force=False):
        """Download and parse json from remote.

        Change remote_url to the manifests @id (which is the
        manifests own description of its URL) if it is at the
        same host as the remote_url posted in.

        :kwargs:
            -force: If true, will fetch resource even if object already
                has it.
        """
        if not self.json or force:
            try:
                manifest_resp = get_doc(self.remote_url)
            except requests.exceptions.Timeout:
                self.errors.append(timeout_error.format(self.remote_url))
                raise ManifestImportError
            manifest_data = manifest_resp.text
            self._generate_manifest_hash(manifest_data)
            self.json = json.loads(manifest_data)

        doc_id = self.json.get("@id")
        if self._compare_url_id(self.remote_url, doc_id):
            self.remote_url = self.json.get('@id')

    def _compare_url_id (self, remote_url, doc_id):
        """Check that rem_url and documents @id have the same netloc.

        :param remote_url (str): Url passed in by user or collection.
        :param doc_id (str): Url at @id in the document.
        :return (bool): True if the urls match, false otherwise.
        """
        rem = parse.urlparse(remote_url)
        doc = parse.urlparse(doc_id)
        if rem[1] != doc[1]:
            return False
        return True

    def _check_db_duplicates(self):
        """Check for duplicates in DB. Delete all but 1. Set
        self.id to the existing duplicate.

        :return True if we already have this exact Manifest, False otherwise.
        """
        old_entry = Manifest.objects.filter(remote_url=self.remote_url)
        if old_entry.count() > 0:
            temp = old_entry[0]
            for man in old_entry:
                if man != temp:
                    man.delete()
            self.db_rep = temp
            self.id = str(temp.id)
            self.in_db = True

            # Don't do anything else if we already have this exact manifest.
            if (self._compare_url_id(self.db_rep.remote_url, self.remote_url) and
                    self.manifest_hash == self.db_rep.manifest_hash):
                temp.save()
                return True
        return False

    def _generate_manifest_hash(self, manifest_text):
        """Set the self.manifest_hash attribute with sha1 hash."""
        self.manifest_hash = hashlib.sha1(manifest_text.encode('utf-8')).hexdigest()

    def _solr_index(self):
        """Parse values from manifest and index in solr"""
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)

        self.doc = {'id': self.id,
                    'type': self.json.get('@type'),
                    'remote_url': self.remote_url,
                    'metadata': []}
        if self.db_rep:
            created = self.db_rep.created
        else:
            created = timezone.now()

        self.doc['created_timestamp'] = created

        multilang_fields = ["description", "attribution", "label",]
        for field in multilang_fields:
            if not self.json.get(field):
                continue

            value = self.json.get(field)
            if type(value) is not list:
                self.doc[field] = value
                continue

            found_default = False
            for v in value:
                if v.get('@language').lower() == "en":
                    self.doc[field] = v.get('@value')
                    found_default = True
                    continue
                key = field + '_txt_' + v.get('@language')
                self.doc[key] = v.get('@value')
            if not found_default:
                v = value[0]
                self.doc[field] = v.get('@value')

        if self.json.get('metadata'):
            meta = self.json.get('metadata')
        else:
            meta = {}

        for m in meta:
            self._add_metadata(m.get('label'), m.get('value'))

        self.doc['manifest'] = json.dumps(self.json)

        """Grabbing either the thumbnail or the first page to index."""
        thumbnail = self.json.get('thumbnail')
        if thumbnail:
            self.doc['thumbnail'] = json.dumps(thumbnail)
        else:
            self._default_thumbnail_setter()

        """Grabbing the logo"""
        logo = self.json.get('logo')
        if logo:
            self.doc['logo'] = json.dumps(logo)

        print("Adding to solr.")
        solr_con.add(self.doc)

    def _add_metadata(self, label, value):
        """Handle adding metadata to the indexed document.

        :param label: The key for this entry in the metadata dict.
        :param value: The values associated with this key.
        :return:
        """

        norm_label = self._meta_label_normalizer(label)

        """The label could not be normalized, and the value is not a list,
        so simply dump the value into the metadata field"""
        if not norm_label and type(value) is not list:
            self.doc['metadata'].append(value)

        """The label could not be normalized but the value has multiple languages.
        Dump known languages into metadata, ignore others"""
        if not norm_label and type(value) is list:
            values = []
            for v in value:
                if type(v) is str:
                    values.append(v)
                elif v.get('@language').lower() in indexed_langs:
                    key = 'metadata_txt_' + v.get('@language').lower()
                    if not self.doc.get(key):
                        self.doc[key] = []
                    self.doc[key].append(v.get('@value'))
            if values:
                self.doc['metadata'].append(" ".join(list(values)))

        """If the label was normalized, and the value is not a list, simply
        add the value to the self.doc with its label"""
        if norm_label and type(value) is not list:
            self.doc[norm_label] = value

        """The label was normalized and the value is a list, add the
        multilang labels and attempt to set english as default, or
        set the first value as default."""
        if norm_label and type(value) is list:
            for v in value:
                if type(v) is str and not self.doc[norm_label]:
                    self.doc[norm_label] = v
                elif type(v) is dict and v.get('@language').lower() == "en":
                    self.doc[norm_label] = v.get("@value")
                elif v.get('@language').lower() in indexed_langs:
                    self.doc[norm_label + "_txt_" + v.get('@language')] = v.get('@value')

    def _default_thumbnail_setter(self):
        """Tries to set thumbnail to an image in the middle of the manifest"""
        tree = ['sequences', 'canvases', 'images']
        branch = self.json
        warning = "Could not find default thumbnail. Tree ends at {0}."
        for key in tree:
            branch = branch.get(key)
            if not branch:
                self.warnings.append(warning.format(key))
                return
            if key == 'canvases':
                branch = branch[int(len(branch)/2)]
            else:
                branch = branch[0]
        resource = branch.get('resource')
        if resource:
            if resource.get('item'):
                del resource['item']
            self.doc['thumbnail'] = json.dumps(resource)

    def _meta_label_normalizer(self, label):
        """Try to find a normalized representation for a label that
        may be a string or list of multiple languages of strings.
        :param label: A string or list of dicts.
        :return: A string; the best representation found.
        """

        if not label:
            return None
        elif type(label) is list:
            # See if there is an English label that can be matched to
            # known fields and return it if it exists.
            for v in label:
                if v.get('@language').lower() == "en":
                    english_label = v.get('@value').lower()
                    repr = settings.SOLR_MAP.get(english_label)
                    if repr:
                        return repr

            # See if there is any label that can be matched to
            # known fields and return it if it exists.
            for v in label:
                repr = settings.SOLR_MAP.get(v.get('@value').lower())
                if repr:
                    return repr

            # Return None if no normalization possible.
            return None

        elif type(label) is str:
            return settings.SOLR_MAP.get(label.lower())
        else:
            raise ManifestImportError("metadata label {0} is not list or str".format(label))

    def _solr_delete(self):
        """ Delete document of self from solr"""
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)
        solr_con.delete_by_ids([self.id])

    def _create_db_entry(self):
        """Create new DB entry with given id"""
        manifest = Manifest(remote_url=self.remote_url,
                            id=self.id, manifest_hash=self.manifest_hash)
        manifest.save()
