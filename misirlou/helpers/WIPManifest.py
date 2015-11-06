import json

import scorched
from urllib.request import urlopen

from django.conf import settings
from misirlou.helpers.validator import Validator
from misirlou.models.manifest import Manifest


class ManifestImportError(Exception):
    pass


class WIPManifest:
    # A class for manifests that are being built
    def __init__(self, remote_url, shared_id):
        self.remote_url = remote_url
        self.id = shared_id
        self.json = {}
        self.meta = []
        self.errors = {'validation': []}
        self.warnings = {}
        self.in_db = False

    def create(self):
        """ Go through the steps of validating and indexing this manifest.
        Return False if error hit, True otherwise."""
        try:
            self.__validate()
            self.__retrieve_json()
            self.__check_db_duplicates()
            self.__solr_index()
        except ManifestImportError:
            return False

        # If check_db_duplicates has found the manifest, if so return now.
        if self.in_db:
            return True

        # otherwise create this manifest in the database.
        try:
            self.__create_db_entry()
        except:
            self.__solr_delete()
            raise
        return True

    def __validate(self):
        """Validate from proper IIIF API formatting"""
        v = Validator(self.remote_url)
        result = v.do_test()
        if result.get('status'):
            self.warnings = result.get('warnings')
            return
        else:
            self.errors = result.get('error')
            raise ManifestImportError

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

    def __solr_index(self):
        """Parse values from manifest and index in solr"""
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)

        document = {'id': self.id,
                    'type': self.json.get('@type'),
                    'remote_url': self.remote_url}

        multilang_fields = ["description", "attribution", "label", "date"]
        for field in multilang_fields:
            if self.json.get(field):
                value = self.json.get(field)
                if type(value) is list:
                    for v in value:
                        if v.get('@language').lower() == 'en':
                            document[field] = v.get('@value')
                        else:
                            key = field + '_' + v.get('@language')
                            document[key] = v.get('@value')
                else:
                    document[field] = value

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
                        if vi.get('@language').lower() == "en":
                            document[label] = vi.get('@value')
                        else:
                            document[label + "_" + vi.get('@language')] \
                                = vi.get('@value')
            document['metadata'] = self.meta

        document['manifest'] = json.dumps(self.json)
        solr_con.add(document)
        solr_con.commit()

    def __solr_delete(self):
        """ Delete document of self from solr"""
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)
        solr_con.delete_by_ids([self.id])
        solr_con.commit()

    def __create_db_entry(self):
        """Create new DB entry with given id"""
        manifest = Manifest(remote_url=self.remote_url, id=self.id)
        manifest.save()
