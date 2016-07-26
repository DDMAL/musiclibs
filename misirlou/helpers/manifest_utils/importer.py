import ujson as json
import uuid
import urllib
import hashlib
import requests
import scorched

import django.core.exceptions as django_exceptions
from django.conf import settings
from django.template.defaultfilters import strip_tags
from django.utils import timezone

from misirlou.models import Manifest

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
        self.text = None
        self.json = {}
        self.type = ""
        self._prepare_for_creation()

    def _prepare_for_creation(self):
        try:
            manifest_resp = get_doc(self.remote_url)
        except requests.exceptions.Timeout:
            self.errors.append(timeout_error.format(self.remote_url))
            return
        self.text = manifest_resp.text

        try:
            self.json = json.loads(self.text)
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


class ManifestImporter:
    # A class for manifests that are being built
    def __init__(self, remote_url, shared_id=None, prefetched_data=None):
        """Create a ManifestImporter

        :param remote_url: URL of IIIF manifest.
        :param shared_id: ID to apply as the manifest's uuid.
        :param prefetched_data: Text of manifest at remote url.
        :return:
        """
        self.remote_url = remote_url
        self.id = shared_id if shared_id else str(uuid.uuid4())
        self.doc = {}  # for solr_indexing
        self.errors = []
        self.warnings = []
        self.in_db = False
        self.db_rep = None
        self.manifest_hash = None
        if prefetched_data:
            self.manifest_hash = self.generate_manifest_hash(prefetched_data)
            self.json = json.loads(prefetched_data)
        else:
            self.json = {}

    def create(self, force=False):
        """ Go through the steps of validating and indexing this manifest.
        Return False if error hit, True otherwise."""
        try:
            self._retrieve_json()  # Get the doc if we don't have it.
            self._find_existing_db_rep()
        except ManifestImportError:
            return False

        # If it's in db and hasn't changed, do nothing.
        if self.in_db and self.db_rep.manifest_hash == self.manifest_hash and not force:
            self.warnings.append("Manifest has not changed since last indexed. No work done.")
            return True

        try:
            self.__validate()
        except ManifestImportError:
            if self.in_db:
                self.db_rep.is_valid = False
                self.db_rep.save()
                self._solr_index()
            return False

        if self.in_db:
            self.db_rep.manifest_hash = self.manifest_hash
            self.db_rep.reset_validity()
            self.db_rep.save()
        else:
            self._create_db_entry()

        self._solr_index()
        return True

    def __validate(self):
        """Validate for proper IIIF API formatting"""
        from misirlou.helpers.manifest_utils.library_specific_exceptions import get_validator
        v = get_validator(self.remote_url)
        v.logger.disabled = True
        v.fail_fast = True
        v.validate(self.json)
        if v.is_valid:
            self.json = v.corrected_doc
            self.warnings.extend(str(warn) for warn in v.warnings)
            return
        else:
            self.errors.extend(str(err) for err in v.errors)
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
            self.manifest_hash = self.generate_manifest_hash(manifest_data)
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
        rem = urllib.parse.urlparse(remote_url)
        doc = urllib.parse.urlparse(doc_id)
        if rem[1] != doc[1]:
            return False
        return True

    def _find_existing_db_rep(self):
        """Check for duplicate in the DB and take its info it if exists.

        :return True if we already have this exact Manifest, False otherwise.
        """
        try:
            old_entry = Manifest.objects.filter(remote_url=self.remote_url).earliest('created')
        except django_exceptions.ObjectDoesNotExist:
            self.in_db = False
            return False
        else:
            self.db_rep = old_entry
            self.id = str(old_entry.id)
            self.in_db = True
            return True

    @staticmethod
    def generate_manifest_hash(manifest_text):
        """Compute and return a hash for the manifest text."""
        return hashlib.sha1(manifest_text.encode('utf-8')).hexdigest()

    def _solr_index(self):
        """Parse values from manifest and index in solr"""
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)

        self.doc = {'id': self.id,
                    'type': self.json.get('@type'),
                    'remote_url': self.remote_url,
                    'is_valid': self.db_rep.is_valid,
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


        """Grabbing either the thumbnail or the first page to index."""
        self.doc['thumbnail'] = self._default_thumbnail_finder()

        """Grabbing the logo"""
        logo = self.json.get('logo')
        if logo:
            self.doc['logo'] = json.dumps(logo)

        self.doc = self._remove_html(self.doc)
        self.doc['manifest'] = json.dumps(self.json)

        solr_con.add(self.doc)

    def _remove_html(self, doc):
        """Return a copy of the doc with html removed from all fields."""
        def recurse(field):
            if isinstance(field, str):
                return strip_tags(field)
            elif isinstance(field, (list)):
                return [recurse(x) for x in field]
            elif isinstance(field, dict):
                return {recurse(k): recurse(v) for k,v in field.items()}
            else:
                return field
        return recurse(doc)

    def _add_metadata(self, label, value):
        """Handle adding metadata to the indexed document.

        :param label: The key for this entry in the metadata dict.
        :param value: The values associated with this key.
        :return:
        """

        norm_label = self._meta_label_normalizer(label)

        """The label could not be normalized, and the value is not a list,
        so simply dump the value into the metadata field"""
        if not norm_label and type(value) is str:
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
        if norm_label and type(value) is str:
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

    def _default_thumbnail_finder(self, force_IIIF=False, index=None):
        """Tries to set thumbnail to an image in the middle of the manifest"""
        if not force_IIIF:
            thumbnail = self.json.get('thumbnail')
            if thumbnail:
                return json.dumps(thumbnail)

        tree = ['sequences', 'canvases', 'images']
        branch = self.json
        warning = "Could not find default thumbnail. Tree ends at {0}."
        for key in tree:
            branch = branch.get(key)
            if not branch:
                self.warnings.append(warning.format(key))
                return
            if key == 'canvases':
                canvas_index = index if index is not None else int(len(branch)/2)
                branch = branch[canvas_index]
            else:
                branch = branch[0]
        resource = branch.get('resource')
        if resource:
            if resource.get('item'):
                del resource['item']
            return json.dumps(resource)

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
        self.db_rep = manifest


def get_importer(uri, prefetched_data=None):
    import misirlou.helpers.manifest_utils.library_specific_exceptions as libraries

    parsed = urllib.parse.urlparse(uri)
    netloc = parsed.netloc

    if netloc == "gallica.bnf.fr":
        importer = libraries.get_gallica_bnf_fr_importer()
    elif netloc == "iiif.archivelab.org":
        importer = libraries.get_archivelab_org_importer()
    else:
        importer = ManifestImporter

    return importer(uri, prefetched_data=prefetched_data)
