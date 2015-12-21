from __future__ import absolute_import

from celery import shared_task
from celery import current_app
from celery.signals import after_task_publish
from django.conf import settings
from .helpers.IIIFImporter import Importer, WIPManifest

import uuid

@shared_task
def create_manifest(remote_url, shared_id, commit=True):
    """Validate, index, and create a database entry for the manifest
    :param remote_url: The manifest's url.
    :param shared_id:  The UUID to be assigned to the manifest.
    """

    imp = Importer(remote_url, shared_id)
    lst = imp.create(commit)

    #There is one manifest to be created.
    if lst and isinstance(lst[0], WIPManifest):
        man = lst[0]
        if man.create() is False:
            create_manifest.update_state(state='ERROR')
            return {'error': man.errors,
                    'status': settings.ERROR}
        else:
            data = {'status': settings.SUCCESS, 'id': man.id}
            if man.warnings['validation'] or len(man.warnings.keys()) > 1:
                data['warnings'] = man.warnings
            if man.errors['validation'] or len(man.errors.keys()) > 1:
                data['errors'] = man.errors
            return data
    if not lst:
        return {'error': 'Could not find manifests.', 'status': settings.ERROR}

    i = 0
    length = len(lst)
    data = {}
    for rem_url in lst:
        man = WIPManifest(rem_url, str(uuid.uuid4()))
        if man.create() is False:
            data[rem_url] = {}
            if man.warnings['validation'] or len(man.warnings.keys()) > 1:
                data[rem_url]['warnings'] = man.warnings
            if man.errors['validation'] or len(man.errors.keys()) > 1:
                data[rem_url]['errors'] = man.errors
        else:
            if man.warnings['validation'] or len(man.warnings.keys()) > 1:
                data[rem_url] = {}
                data[rem_url]['warnings'] = man.warnings
        i += 1
        create_manifest.update_state(state=settings.PROGRESS, meta={'current': i, 'total': length})

@after_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):
    # Change task.status to 'SENT' for all tasks which are sent in.
    # This allows one to distinguish between PENDING tasks which have been
    # sent in and tasks which do not exist. State will change to
    # SUCCESS, FAILURE, etc. once the process terminates.
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    backend.store_result(body['id'], None, "SENT")
