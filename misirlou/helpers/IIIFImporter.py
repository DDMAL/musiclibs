import ujson as json
import scorched
from urllib.request import urlopen

from django.conf import settings
from misirlou.helpers.validator import Validator
from misirlou.models.manifest import Manifest


indexed_langs = ["en", "fr", "it", "de"]


class ManifestImportError(Exception):
    pass


class Importer:
    def __init__(self, remote_url, shared_id):
        self.remote_url = remote_url
        self.id = shared_id
        self.errors = {"validation": []}
        self.warnings = {'validation': []}
        self.json = {}
        self.type = ""
        self._prepare_for_creation()

    def _prepare_for_creation(self):
        manifest_resp = urlopen(self.remote_url)
        manifest_data = manifest_resp.read().decode('utf-8')
        self.json = json.loads(manifest_data)

        self.type = self.json.get('@type')
        if not self.type:
            self.errors['validation'].append("Validation: Document has no @type.")
            return

        self.remote_url = self.json.get("@id")
        if not self.remote_url:
            self.warnings['validation'].append("Validation: Document has no @tid.")
            return

    def create(self, commit=True):
        if len(self.errors.keys()) > 1 or self.errors['validation']:
            return False

        if self.type == "sc:Manifest":
            m = WIPManifest(self.remote_url, self.id)
            m.json = self.json
            return [m]

        elif self.type == "sc:Collection":
            return self.get_all_manifests(self.json)

    def get_all_manifests(self, json_obj, manifest_set=set()):
        manifests = json_obj.get('manifests', {})
        for man in manifests:
            tmp_url = man.get("@id")
            if(tmp_url):
                manifest_set.add(tmp_url)

        collections = self.json.get('collections', {})
        for col in collections:
            col_url = col.get("@id")
            if not col_url:
                continue
            col_resp = urlopen(col_url)
            col_data = col_resp.read().decode('utf-8')
            col_json = json.loads(col_data)
            self.get_all_manifests(col_json, manifest_set)
        return list(manifest_set)


class WIPManifest:
    # A class for manifests that are being built
    def __init__(self, remote_url, shared_id):
        self.remote_url = remote_url
        self.id = shared_id
        self.json = {}
        self.meta = []
        self.errors = {'validation': []}
        self.warnings = {'validation': []}
        self.in_db = False

    def create(self, commit=True):
        """ Go through the steps of validating and indexing this manifest.
        Return False if error hit, True otherwise."""
        try:
            self.__validate()
            if not self.json:
                self._retrieve_json()
            self._check_db_duplicates()
            self._solr_index(commit)
        except ManifestImportError:
            return False

        # If check_db_duplicates has found the manifest, if so return now.
        if self.in_db:
            return True

        # otherwise create this manifest in the database.
        try:
            self._create_db_entry()
        except:
            self._solr_delete()
            raise
        return True

    def __validate(self):
        """Validate from proper IIIF API formatting"""
        v = Validator(self.remote_url)
        result = v.do_test()
        if result.get('status'):
            self.warnings['validation'].append(result.get('warnings'))
            return
        else:
            self.errors = result.get('error')
            raise ManifestImportError

    def _retrieve_json(self):
        """Download and parse json from remote.
        Change remote_url to the manifests @id (which is the
        manifests own description of its URL)"""
        manifest_resp = urlopen(self.remote_url)
        manifest_data = manifest_resp.read().decode('utf-8')
        self.json = json.loads(manifest_data)
        self.remote_url = self.json.get('@id')

    def _check_db_duplicates(self):
        """Check for duplicates in DB. Delete all but 1. Set
        self.id to the existing duplicate."""
        old_entry = Manifest.objects.filter(remote_url=self.remote_url)
        if old_entry.count() > 0:
            temp = old_entry[0]
            for man in old_entry:
                if man != temp:
                    man.delete()
            temp.save()
            self.id = str(temp.id)
            self.in_db = True

    def _solr_index(self, commit=True):
        """Parse values from manifest and index in solr"""
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)

        document = {'id': self.id,
                    'type': self.json.get('@type'),
                    'remote_url': self.remote_url,
                    'metadata': []}

        multilang_fields = ["description", "attribution", "label",]
        for field in multilang_fields:
            if not self.json.get(field):
                continue

            value = self.json.get(field)
            if type(value) is not list:
                document[field] = value
                continue

            found_default = False
            for v in value:
                if v.get('@language').lower() == "en":
                    document[field] = v.get('@value')
                    found_default = True
                    continue
                key = field + '_txt_' + v.get('@language')
                document[key] = v.get('@value')
            if not found_default:
                v = value[0]
                document[field] = v.get('@value')

        if self.json.get('metadata'):
            meta = self.json.get('metadata')
        else:
            meta = {}

        for m in meta:
            self._add_metadata(m.get('label'), m.get('value'), document)

        document['manifest'] = json.dumps(self.json)

        """Grabbing either the thumbnail or the first page to index."""
        thumbnail = self.json.get('thumbnail')
        if thumbnail:
            document['thumbnail'] = json.dumps(thumbnail)
        else:
            self._default_thumbnail_setter(document)

        """Grabbing the logo"""
        logo = self.json.get('logo')
        if logo:
            document['logo'] = json.dumps(logo)

        solr_con.add(document)

        if commit:
            solr_con.commit()


    def _add_metadata(self, label, value, document):

        norm_label = self._meta_label_normalizer(label)

        """The label could not be normalized, and the value is not a list,
        so simply dump the value into the metadata field"""
        if not norm_label and type(value) is not list:
            document['metadata'].extend([label, value])

        """The label could not be normalized but the value has multiple languages.
        Dump known languages into metadata, ignore others"""
        if not norm_label and type(value) is list:
            vset = set()
            for v in value:
                if type(v) is str:
                    vset.add(v)
                elif v.get('@language').lower() in indexed_langs:
                    key = 'metadata_txt_' + v.get('@language').lower()
                    if not document.get(key):
                        document[key] = []
                    document[key].append(v.get('@value'))
            if vset:
                document['metadata'].extend([label, list(vset)])

        """If the label was normalized, and the value is not a list, simply
        add the value to the document with its label"""
        if norm_label and type(value) is not list:
            if self._is_distinct_field(norm_label):
                document[norm_label] = value
            else:
                document['metadata'].extend([norm_label, value])

        """The label was normalized and the value is a list, add the
        multilang labels and attempt to set english as default, or
        set the first value as default."""
        if norm_label and type(value) is list:
            found_default = False
            if self._is_distinct_field(norm_label):
                vset = set()
                for v in value:
                    if type(v) is str:
                        vset.add(v)
                        found_default = True
                    elif type(v) is dict and v.get('@language').lower() == "en":
                        vset.add(v.get("@value"))
                        found_default = True
                    elif v.get('@language').lower() in indexed_langs:
                        document[label + "_txt_" + v.get('@language')] \
                            = v.get('@value')

                if found_default:
                    document[norm_label] = list(vset)

            else:
                vset = set()
                for v in value:
                    vset.add(v)
                document['metadata'].extend([norm_label, list(vset)])


    def _default_thumbnail_setter(self, document):
        """Tries to set the thumbnail to the first image in the manifest"""
        tree = ['sequences', 'canvases', 'images']
        branch = self.json
        warning = "Could not find default thumbnail. Tree ends at {0}."
        for key in tree:
            branch = branch.get(key)
            if not branch:
                self.warnings['thumbnail'] = warning.format(key)
                return
            branch = branch[0]
        if branch.get('resource'):
            document['thumbnail'] = json.dumps(branch.get('resource'))

    def _meta_label_normalizer(self, label):
        """Try to find a normalized representation for a label that
        may be a string or list of multiple languages of strings.
        :param label: A string or list of dicts.
        :return: A string; the best representation found, or nothing
        if no normalization was possible.
        """

        if not label:
            return None
        if type(label) is list:
            for v in label:
                if v.get('@language').lower() == "en":
                    repr = settings.SOLR_MAP.get(v.get('@value').lower())
                    if repr:
                        return repr
                    else:
                        v.get('@value').lower()
            for v in label:
                repr = settings.SOLR_MAP.get(v.get('@value').lower())
                if repr:
                    return repr
            if type(label[0]) is str:
                return label[0].lower()
            else:
                return label[0].get('@value').lower()
        else:
            return settings.SOLR_MAP.get(label.lower())

    def _is_distinct_field(self, label):
        if settings.SOLR_MAP.get(label):
            return True
        return False

    def _solr_delete(self):
        """ Delete document of self from solr"""
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)
        solr_con.delete_by_ids([self.id])
        solr_con.commit()

    def _create_db_entry(self):
        """Create new DB entry with given id"""
        manifest = Manifest(remote_url=self.remote_url, id=self.id)
        manifest.save()