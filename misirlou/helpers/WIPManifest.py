import json
import scorched
from urllib.request import urlopen
from urllib.parse import urlparse

from django.conf import settings
from misirlou.models.manifest import Manifest

class ManifestImportError(Exception):
    pass

class WIPManifest:
    # A class for manifests that are being built
    def __init__(self, remote_url, shared_id):
        self.remote_url = remote_url
        self.uuid = shared_id
        self.json = {}
        self.meta = []
        self.errors = {'validation': []}
        self.warnings = {}
        self.in_db = False

    def create(self):
        """ Go through the steps of validating and indexing this manifest.
        Return False if error hit, True otherwise."""
        try:
            self.__parse_remote_url()
            self.__retrieve_json()
            self.__validate_online()
            self.__check_db_duplicates()
            self.__solr_index()
        except ManifestImportError:
            return False

        # check_db has found the manifest, if so return now.
        if self.in_db:
            return True

        # create this manifest in the database.
        try:
            self.__create_db_entry()
        except:
            self.__solr_delete()
            raise
        return True

    def __parse_remote_url(self):
        scheme = 0
        netloc = 1
        purl = urlparse(self.remote_url)
        if not purl[scheme]:
            self.errors['validation'].append("remote_url has no scheme.")
            raise ManifestImportError
        if not purl[netloc]:
            self.errors['validation'].append("remote_url invalid.")
            raise ManifestImportError

    def __validate_online(self):
        pass
        # v_url = "http://iiif.io/api/presentation/validator/service/validate" \
        #         "?format=json&version=2.0&url="
        # v_resp = urllib.request.urlopen(v_url + self.url)
        # v_data = v_resp.read().decode('utf-8')
        # v_data = json.loads(v_data)
        #
        #  if v_data.get('error') != "None":
        #     self.errors['validation'] = v_data.get('error')
        # 
        # if v_data.get('warnings') != "None":
        #    self.warnings['validation'] = v_data.get('warnings')

    def __retrieve_json(self):
        """Download and parse json from remote.
        Change remote_url to the manifests @id (which is the
        manifests own description of its URL)"""
        manifest_resp = urlopen(self.remote_url)
        manifest_data = manifest_resp.read().decode('utf-8')
        self.json = json.loads(manifest_data)
        self.remote_url = self.json.get('@id')

    def __check_db_duplicates(self):
        """Check for duplicates in DB. Delete all but 1. Set
        self.uuid to the existing duplicate."""
        old_entry = Manifest.objects.filter(remote_url=self.remote_url)
        if old_entry.count() > 0:
            temp = old_entry[0]
            for man in old_entry:
                if man != temp:
                    man.delete()
            temp.save()
            self.uuid = str(temp.uuid)
            self.in_db = True

    def __solr_index(self):
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)

        # delete documents in solr with the same remote_url
        solr_con.delete_by_query(query=solr_con.Q(remote_url=self.remote_url))

        document = {'id': self.uuid,
                    'type': self.json.get('@type'),
                    'label': self.json.get('label'),
                    'remote_url': self.remote_url}

        if self.json.get('description'):
            description = self.json.get('description')
            if type(description) is list:
                for d in description:
                    key = 'description_' + d.get('@language')
                    document[key] = d.get('@value')
            else:
                key = 'description'
                document[key] = description

        if self.json.get('metadata'):
            meta = self.json.get('metadata')
            for m in meta:
                label = settings.SOLR_MAP.get(m.get('label').lower())
                value = m.get('value')
                if not label and type(value) is not list:
                    self.meta.append(m.get('value'))
                if not label and type(value) is list:
                    for vi in value:
                        self.meta.append(vi.get('@value'))
                if label and type(value) is not list:
                    document[label] = value
                if label and type(value) is list:
                    for vi in value:
                        document[label + "_" + vi.get('@language')] \
                            = vi.get('@value')
            document['metadata'] = self.meta

        document['manifest'] = json.dumps(self.json)
        solr_con.add(document)
        solr_con.commit()

    def __solr_delete(self):
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)
        solr_con.delete_by_ids([self.uuid])
        solr_con.commit()

    def __create_db_entry(self):
        """Create new DB entry with given uuid"""
        manifest = Manifest(remote_url=self.remote_url, uuid=self.uuid)
        manifest.save()
