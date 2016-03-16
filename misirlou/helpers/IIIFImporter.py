import ujson as json
import scorched
from celery import group

from urllib.request import urlopen
from urllib import parse
from django.conf import settings
from django.utils import timezone
from misirlou.models.manifest import Manifest
from misirlou.helpers.IIIFSchema import ManifestValidator



indexed_langs = ["en", "fr", "it", "de"]


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
        self.errors = {"validation": []}
        self.json = {}
        self.type = ""
        self._prepare_for_creation()

    def _prepare_for_creation(self):
        manifest_resp = urlopen(self.remote_url)
        manifest_data = manifest_resp.read().decode('utf-8')

        try:
            self.json = json.loads(manifest_data)
        except ValueError:
            self.errors['validation'].append("Retrieved document is not valid JSON.")
            return

        self.type = self.json.get('@type')
        if not self.type:
            self.errors['validation'].append("Parsed document has no @type.")
            return

        self.remote_url = self.json.get("@id")
        if not self.remote_url:
            self.errors['validation'].append("Parsed document has no @tid.")
            return

    def get_all_urls(self):
        """Get all the importable URLs related to the remote_url.

        :return: List of strings with importable URLs.
        """
        if len(self.errors.keys()) > 1 or self.errors['validation']:
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

        manifests = json_obj.get('manifests', {})
        for man in manifests:
            tmp_url = man.get("@id")
            if(tmp_url):
                manifest_set.add(tmp_url)

        collections = json_obj.get('collections', {})
        for col in collections:
            col_url = col.get("@id")
            if not col_url:
                continue
            col_resp = urlopen(col_url)
            col_data = col_resp.read().decode('utf-8')
            col_json = json.loads(col_data)
            self._get_nested_manifests(col_json, manifest_set)

        return list(manifest_set)


class ConcurrentManifestImporter:
    """Imports a list of manifests concurrently.

    import_collection() will start many subtasks in order to
    """
    def __init__(self, shared_id):
        self.shared_id = shared_id
        self.processed = 0
        self.length = 0
        self.failed_count = 0
        self.succeeded_count = 0
        self.data = {'failed': {}, 'succeeded': {}}
        self.solr_con = scorched.SolrInterface(settings.SOLR_SERVER)

    def import_collection(self, lst):
        """Import all manifests in lst concurrently.

        :param lst: A list of strings which are expected to be URL's to IIIF Manifests.
        :return: dict of results from sub_tasks.
        """
        from misirlou.tasks import import_single_manifest, import_manifest

        self.length = len(lst)
        group_task = group(import_single_manifest.s(rem_url) for rem_url in lst).apply_async()

        for incoming in group_task.iter_native():
            self.processed += 1
            result = incoming[1]['result']
            status, man_id, rem_url, errors = result

            if status == settings.SUCCESS:
                self.succeeded_count += 1
                self.data['succeeded'][rem_url] = {'status': status, 'uuid': man_id, 'url': '/manifests/{}'.format(man_id)}

            if errors:
                self.failed_count += 1
                self.data['failed'][rem_url] = {'errors': errors, 'status': status, 'uuid': man_id}

            import_manifest.update_state(task_id=self.shared_id,
                                         state=settings.PROGRESS,
                                         meta={'current': self.processed, 'total': self.length})
        self.solr_con.commit()
        self.data['status'] = settings.SUCCESS if self.succeeded_count else settings.ERROR
        self.data['total_count'] = self.length
        self.data['succeeded_count'] = self.succeeded_count
        self.data['failed_count'] = self.failed_count
        return self.data


class WIPManifest:
    # A class for manifests that are being built
    def __init__(self, remote_url, shared_id):
        self.remote_url = remote_url
        self.id = shared_id
        self.json = {}  # retrieved from remote_url
        self.doc = {}  # for solr_indexing
        self.errors = {'validation': []}
        self.in_db = False
        self.db_rep = None

    def create(self, commit=True):
        """ Go through the steps of validating and indexing this manifest.
        Return False if error hit, True otherwise."""
        try:
            if not self.json:
                self._retrieve_json()
            self.__validate()
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
        """Validate for proper IIIF API formatting"""
        v = ManifestValidator()
        v.validate(self.json)
        if v.is_valid:
            return
        else:
            self.errors['validation'].append(v.errors)
            raise ManifestImportError

    def _retrieve_json(self):
        """Download and parse json from remote.
        Change remote_url to the manifests @id (which is the
        manifests own description of its URL) if it is at the
        same host as the remote_url posted in."""
        manifest_resp = urlopen(self.remote_url)
        manifest_data = manifest_resp.read().decode('utf-8')
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
        self.id to the existing duplicate."""
        old_entry = Manifest.objects.filter(remote_url=self.remote_url)
        if old_entry.count() > 0:
            temp = old_entry[0]
            for man in old_entry:
                if man != temp:
                    man.delete()
            self.db_rep = temp
            self.id = str(temp.id)
            self.in_db = True

    def _solr_index(self, commit=True):
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

        solr_con.add(self.doc)

        if commit:
            solr_con.commit()

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
            vset = set()
            for v in value:
                if type(v) is str:
                    vset.add(v)
                elif v.get('@language').lower() in indexed_langs:
                    key = 'metadata_txt_' + v.get('@language').lower()
                    if not self.doc.get(key):
                        self.doc[key] = []
                    self.doc[key].append(v.get('@value'))
            if vset:
                self.doc['metadata'].append(" ".join(list(vset)))

        """If the label was normalized, and the value is not a list, simply
        add the value to the self.doc with its label"""
        if norm_label and type(value) is not list:
            if self._is_distinct_field(norm_label):
                self.doc[norm_label] = value
            else:
                self.doc['metadata'].append(value)

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
                        self.doc[label + "_txt_" + v.get('@language')] \
                            = v.get('@value')

                if found_default:
                    self.doc[norm_label] = list(vset)

            else:
                vset = set()
                for v in value:
                    vset.add(v)
            self.doc['metadata'].append(" ".join(list(vset)))

    def _default_thumbnail_setter(self):
        """Tries to set the thumbnail to the first image in the manifest"""
        tree = ['sequences', 'canvases', 'images']
        branch = self.json
        warning = "Could not find default thumbnail. Tree ends at {0}."
        for key in tree:
            branch = branch.get(key)
            if not branch:
                return
            branch = branch[0]
        if branch.get('resource'):
            self.doc['thumbnail'] = json.dumps(branch.get('resource'))

    def _meta_label_normalizer(self, label):
        """Try to find a normalized representation for a label that
        may be a string or list of multiple languages of strings.
        :param label: A string or list of dicts.
        :return: A string; the best representation found, or nothing
        if no normalization was possible.
        """

        if not label:
            return None
        elif type(label) is list:
            english_label = None
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

            # Return the english label (that was not matched to a known
            # field) if it exists.
            if english_label:
                return english_label

            # If all above fails, return the first label.
            if type(label[0]) is str:
                return label[0].lower()
            else:
                return label[0].get('@value').lower()

        elif type(label) is str:
            return settings.SOLR_MAP.get(label.lower())
        else:
            raise ManifestImportError("metadata label {0} is not list or str".format(label))

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