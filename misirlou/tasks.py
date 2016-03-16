from __future__ import absolute_import

import uuid

from celery import shared_task
from celery import current_app
from celery.signals import after_task_publish
from django.conf import settings
from collections import namedtuple

from .helpers.IIIFImporter import ManifestPreImporter, WIPManifest, ConcurrentManifestImporter

# A named tuple for passing task-results from importing Manifests.
ImportResult = namedtuple('ImportResult', ['status', 'id', 'url', 'errors', 'warnings'])


@shared_task
def import_manifest(remote_url, shared_id, commit=True):
    """Handle importing of Manifests and Collections.

    This is the entry point for all actions done on import.

    :param remote_url: A manifest or collection url.
    :param shared_id:  The UUID to be assigned to the manifest.
    """

    imp = ManifestPreImporter(remote_url)
    lst = imp.get_all_urls()

    if lst:
        c = ConcurrentManifestImporter(shared_id)
        return c.import_collection(lst)
    else:
        return {'error': 'Could not find manifests.', 'status': settings.ERROR}


@shared_task
def import_single_manifest(remote_url):
    man = WIPManifest(remote_url, str(uuid.uuid4()))
    errors = []
    warnings = []
    rem_url = remote_url
    man_id = man.id

    try:
        imp_success = man.create(False)
    except Exception as e:
        imp_success = False
        errors.append(str(e))

    if imp_success:
        warnings.extend(man.warnings)
        status = settings.SUCCESS
    else:
        warnings.extend(man.warnings)
        errors.extend(man.errors)
        status = settings.ERROR

    return ImportResult(status, man_id, rem_url, errors, warnings)


@after_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):
    # Change task.status to 'SENT' for all tasks which are sent in.
    # This allows one to distinguish between PENDING tasks which have been
    # sent in and tasks which do not exist. State will change to
    # SUCCESS, FAILURE, etc. once the process terminates.
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    backend.store_result(body['id'], None, "SENT")
