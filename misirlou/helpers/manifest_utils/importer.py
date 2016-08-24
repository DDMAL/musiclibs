import ujson as json
import uuid
import urllib
import hashlib
import requests
import scorched
import datetime
from collections import defaultdict

import django.core.exceptions as django_exceptions
from django.conf import settings
from django.template.defaultfilters import strip_tags
from django.utils import timezone

from misirlou.models import Manifest
from misirlou.signals import manifest_imported
from misirlou.helpers.manifest_utils.errors import ErrorMap
from misirlou.helpers.manifest_utils.utils import get_language

indexed_langs = ["en", "fr", "it", "de"]
timeout_error = "Timed out fetching '{}'"
ERROR_MAP = ErrorMap()


def get_doc(remote_url):
    """Get a document using requests."""
    return requests.get(remote_url, verify=False, timeout=20)


class ManifestImportError(Exception):
    """Catch-all error to end import and clean up."""
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
    """Class to import Manifests from a remote url.

    create() handles retrieval, validation, parsing and indexing of a manifest.
    """

    def __init__(self, remote_url, shared_id=None, prefetched_data=None):
        """Create a ManifestImporter.

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
        self.db_rep = None
        self.manifest_hash = ""
        if prefetched_data:
            self.manifest_hash = self.generate_manifest_hash(prefetched_data)
            self.json = json.loads(prefetched_data)
        else:
            self.json = {}

    def create(self, force=False):
        """ Go through the steps of validating and indexing this manifest.

        Return False if error hit, True otherwise."""
        # Find existing db rep, or create one.
        in_db = self._find_existing_db_rep()
        if not in_db:
            man = Manifest(remote_url=self.remote_url, id=self.id,
                           manifest_hash=self.manifest_hash, indexed=False)
            man.save()
            self.db_rep = man

        # Get the doc if we don't have it.
        try:
            self._retrieve_json()
        except ManifestImportError:
            return self._exit(ERROR_MAP['FAILED_REMOTE_RETRIEVAL'].code)

        # If it's in db, is indexed, and hasn't changed, then do nothing.
        if self.db_rep.manifest_hash == self.manifest_hash \
                and self.db_rep.indexed\
                and not force:
            self.warnings.append("Manifest has not changed since last indexed. No work done.")
            return True

        # Validate the manifest and mark it as invalid if it fails.
        try:
            self.__validate()
        except ManifestImportError:
            return self._exit(ERROR_MAP['FAILED_VALIDATION'].code)

        self._solr_index()
        self.db_rep.manifest_hash = self.manifest_hash
        self.db_rep.indexed = True
        self.db_rep.source = self._find_source()
        self.db_rep.reset_validity()
        self.db_rep.save()

        self.alert_succeeded_import()
        return True

    def _exit(self, error_code):
        """Make sure record of failed import is saved and return false."""
        if self.db_rep:
            self.db_rep.is_valid = False
            self.db_rep.error = error_code
            self.db_rep.last_tested = datetime.datetime.now()

            if self.db_rep.indexed:
                self.db_rep._update_solr_validation()
            self.db_rep.save()
        return False

    def alert_succeeded_import(self):
        """Dispatch an import signal."""
        manifest_imported.send(sender=self.__class__, id=str(self.id), local_url=self.db_rep.get_absolute_url())

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

        Use the netloc and path of the given url as a search for an existing
        manifest. If one is found, upgrade its url to https if possible.

        Assumes that all manifest url's will be http or https and will not have query parameters.

        :return True if we already have this exact Manifest, False otherwise.
        """
        parsed = urllib.parse.urlparse(self.remote_url)
        new_scheme = parsed[0]
        netloc_and_path = "".join(parsed[1:3])
        try:
            old_entry = Manifest.objects.get(remote_url__contains=netloc_and_path)
            parsed2 = urllib.parse.urlparse(old_entry.remote_url)
            old_scheme = parsed2[0]
            if old_scheme == 'http' and new_scheme == 'https':
                old_entry.remote_url = self.remote_url
                old_entry.save()
            else:
                self.remote_url = old_entry.remote_url
        except django_exceptions.ObjectDoesNotExist:
            return False
        except django_exceptions.MultipleObjectsReturned:
            raise django_exceptions.MultipleObjectsReturned("More than one manifest exists in the database with this remote_url!")
        else:
            self.db_rep = old_entry
            self.id = str(old_entry.id)
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
                if get_language(v).startswith("en"):
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

        mp = IIIFMetadataParser(meta)
        parsed_metadata = mp.parse_for_solr()
        for key, val in parsed_metadata.items():
            current_val = self.doc.get(key, [])
            if not isinstance(current_val, list):
                current_val = [current_val]
            current_val.extend(val)
            self.doc[key] = current_val

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

    def _find_source(self):
        """Try to find a source this manifest belongs to.

        If none can be found, a source will be created and attached.
        """
        from misirlou.models import Source
        return Source.get_source(self.json)

    def _solr_delete(self):
        """ Delete document of self from solr"""
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)
        solr_con.delete_by_ids([self.id])


class IIIFMetadataParser:

    # Map where each key has a list of synonyms as it's value.
    # This map is reversed (each value points to its key) and saved
    # as LABEL_MAP.
    __reversed_map = {
        'title': ['title', 'titles', 'title(s)', 'titre', 'full title'],
        'author': ['author', 'authors', 'author(s)', 'creator'],
        'date': ['date', 'period', 'publication date', 'publish date'],
        'location': ['location'],
        'language': ['language'],
        'repository': ['repository']
    }

    LABEL_MAP = {}
    for k, v in __reversed_map.items():
        for vi in v:
            LABEL_MAP[vi] = k

    def __init__(self, metadata_list):
        self.original_metadata = metadata_list
        self._normalized_metadata = self.normalize_metadata(metadata_list)

    def parse_for_solr(self, metadata_list=None):
        if metadata_list is None:
            metadata_list = self._normalized_metadata
        normalized_metadata = self.normalize_metadata(metadata_list)
        metadata = defaultdict(list)

        for entry in normalized_metadata:
            label = entry['label']
            value = entry['value']
            normalized_label = self._normalize_label(label)
            parsed_values = self._parse_value(value, normalized_label)

            for key, val in parsed_values.items():
                metadata[key].extend(val)
        return metadata

    def _parse_value(self, value, label=None):
        """Parse a value list into a dict for solr.

        Given a value list, iterate through it and construct a dictionary
        which is ready to be passed into solr.

        :param value: A list of {'@language': str, '@value': str} dicts.
        :param label: A label to be applied to this value (defaults to 'metadata')
        :return A dict of label,value pairs (with language information in label)
        """
        result = defaultdict(list)
        label = label if label is not None else 'metadata'
        found_english = False

        # Loop over once to try to find an english values for the default.
        for val in value:
            at_lang = val['@language']
            if at_lang.startswith('en'):
                found_english = True
                result[label + "_txt_en"].append(val['@value'])
                result[label].append(val['@value'])

        # Strip the english values if they've already been found and added.
        if found_english:
            value = filter(lambda x: False if x['@language'].startswith('en') else True, value)

        # Add the remaining values.
        for val in value:
            at_lang = val['@language']
            at_val = val['@value']
            if at_lang != '':
                result[label + "_txt_" + at_lang].append(at_val)
            elif found_english:
                result[label + "_txt_un"].append(at_val)
            else:
                result[label].append(at_val)

        return result

    def _normalize_label(self, label):
        """Try to find a normalized label using self.LABEL_MAP.

        :param label: A list of {'@language': str, '@value': str} dicts.
        :return A str if normalization found, else None.
        """
        non_en_norm = None
        for l in label:
            label_language = l['@language'].lower()
            label_value = l['@value'].lower()

            if label_language.startswith('en'):
                norm_label = self.LABEL_MAP.get(label_value)
                if norm_label:
                    return norm_label
            elif label_value in self.LABEL_MAP:
                non_en_norm = self.LABEL_MAP[label_value]
        return non_en_norm

    def normalize_metadata(self, metadata_list):
        """Normalize the metadata representation to a predicable format.

        IIIF Manifest metadata can be represented in a number of ways (which
        can be combined), making it difficult to parse. This function computes
        a normalized representation which looks like the following:
        [
            {
                'value': [
                    {
                        '@value': str,
                        '@language': str
                    },
                    ...
                ],
                'label': [
                    {
                        '@value': str,
                        '@language': str
                    },
                    ...
                ]
            },
            ...
        ]

        That is, each entry has a 'value' and 'label' key which is always a list,
        and each entry in this list always has a '@value' and '@language' key, even
        if these turn out to be unknown (empty strings).
        """
        result_list = []

        def normalize_jsonld_value(value):
            if isinstance(value, str):
                return [{'@language': '', '@value': value}]
            if isinstance(value, dict):
                at_value = value.get('@value')
                at_language = value.get('@language', '')
                return [{'@language': at_language, '@value': at_value}]
            if isinstance(value, list):
                result_list = []
                for val in value:
                    result_list.extend(normalize_jsonld_value(val))
                return result_list
            raise TypeError("JSONLD value must be str, dict, or list.")

        for entry in metadata_list:
            normalized_value = normalize_jsonld_value(entry.get('value'))
            normalized_label = normalize_jsonld_value(entry.get('label'))
            result_list.append({'label': normalized_label, 'value': normalized_value})

        return result_list


def get_importer(uri, prefetched_data=None):
    """Return a ManifestImporter with settings for a specific library."""
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
