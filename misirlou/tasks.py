from __future__ import absolute_import

from celery import shared_task
from celery import current_app
from celery.signals import after_task_publish
from .models.manifest import Manifest
import uuid

@shared_task
def create_manifest(remote_url, shared_id):
    manifest = Manifest(remote_url=remote_url, uuid=uuid.UUID(shared_id))
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