from __future__ import absolute_import

from celery import shared_task
from celery import current_app
from celery.signals import after_task_publish
from django.conf import settings
from .helpers.WIPManifest import WIPManifest

@shared_task
def create_manifest(remote_url, shared_id):
    """Validate, index, and create a database entry for the manifest
    :param remote_url: The manifest's url.
    :param shared_id:  The UUID to be assigned to the manifest.
    """

    wip_man = WIPManifest(remote_url, shared_id)

    if not wip_man.create():
        create_manifest.update_state(state='ERROR')
        return {'error': wip_man.errors,
                'status': settings.ERROR}

    data = {'status': settings.SUCCESS, 'id': wip_man.id}
    if wip_man.warnings:
        data['warnings'] = wip_man.warnings
    return data


@after_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):
    # Change task.status to 'SENT' for all tasks which are sent in.
    # This allows one to distinguish between PENDING tasks which have been
    # sent in and tasks which do not exist. State will change to
    # SUCCESS, FAILURE, etc. once the process terminates.
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    backend.store_result(body['id'], None, "SENT")
