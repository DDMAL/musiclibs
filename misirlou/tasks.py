from __future__ import absolute_import

from celery import shared_task
from celery import current_app
from celery.signals import after_task_publish
from .models.manifest import Manifest
from django.conf import settings
import urllib.request
import json
import scorched

@shared_task
def create_manifest(remote_url, shared_id):
    """Validate, index, and create a database entry for the manifest
    :param remote_url: The manifest's url.
    :param shared_id:  The UUID to be assigned to the manifest.
    """

    wip_man = WIPManifest(remote_url, shared_id)
    wip_man.validate_online()
    if wip_man.errors.get('validation'):
        create_manifest.update_state(state='FAILURE')
        return {'error': wip_man.errors.get('validation')}

    wip_man.solr_index()

    wip_man.create_db_entry()

    data = {'status': 'SUCCESS'}
    if wip_man.warnings:
        data['warnings'] = wip_man.warnings
    return data

class WIPManifest:
    # A class for manifests that are being built
    def __init__(self, url, shared_id):
        self.url = url
        self.id = shared_id
        self.json = {}
        self.errors = {}
        self.warnings = {}

    def validate_online(self):
        v_url = "http://iiif.io/api/presentation/validator/service/validate" \
                "?format=json&version=2.0&url="
        v_resp = urllib.request.urlopen(v_url + self.url)
        v_data = v_resp.read().decode('utf-8')
        v_data = json.loads(v_data)

        if v_data.get('error') != "None":
            self.errors['validation'] = v_data.get('error')

        if v_data.get('warnings') != "None":
            self.warnings['validation'] = v_data.get('warnings')

    def __retrieve_json(self):
        manifest_resp = urllib.request.urlopen(self.url)
        manifest_data = manifest_resp.read().decode('utf-8')
        self.json = json.loads(manifest_data)

    def solr_index(self):
        self.__retrieve_json()
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)
        document = {'id': self.id,
                    'label': self.json.get('label')}

        solr_con.add(document)
        solr_con.commit()

    def create_db_entry(self):
        manifest = Manifest(remote_url=self.url, uuid=self.id)
        manifest.save()


@after_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):
    # Change task.status to 'SENT' for all tasks which are sent in.
    # This allows one to distinguish between PENDING tasks which have been
    # sent in and tasks which do not exist. State will change to
    # SUCCESS, FAILURE, etc. once the process terminates.
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    backend.store_result(body['id'], None, "SENT")