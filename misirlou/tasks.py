from __future__ import absolute_import

from celery import shared_task
from celery.app.task import Task
from celery import current_app
from celery.signals import after_task_publish
from .models.manifest import Manifest
import uuid
import urllib.request
import json

@shared_task
def create_manifest(remote_url, shared_id):
    #Temporarily using online validator.
    #TODO port IIIF validator to py3
    #TODO fix url formatting issues (check for 'http://')
    v_url = "http://iiif.io/api/presentation/validator/service/validate" \
            "?format=json&version=2.0&url="
    v_resp = urllib.request.urlopen(v_url + remote_url)
    v_data = v_resp.read().decode('utf-8')
    v_res = json.loads(v_data)

    if v_res['error'] != "None":
        create_manifest.update_state(state='FAILURE')
        return {'error': v_res['error'], 'warnings': v_res.get('warnings')}

    manifest = Manifest(remote_url=remote_url, uuid=uuid.UUID(shared_id))
    manifest.save()
    if v_res['warnings'] != "None":
        return {'warnings': v_res.get('warnings')}


@after_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):
    # Change task.status to 'SENT' for all tasks which are sent in.
    # This allows one to distinguish between PENDING tasks which have been
    # sent in and tasks which do not exist. State will change to
    # SUCCESS, FAILURE, etc. once the process terminates.
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    backend.store_result(body['id'], None, "SENT")