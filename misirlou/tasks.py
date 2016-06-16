from __future__ import absolute_import

from celery import shared_task
from celery import current_app
from celery.signals import after_task_publish
from django.conf import settings
from collections import namedtuple

from.models.manifest import Manifest
from .helpers.manifest_utils.importer import ManifestImporter

# A named tuple for passing task-results from importing Manifests.
ImportResult = namedtuple('ImportResult', ['status', 'id', 'url', 'errors', 'warnings'])


@shared_task
def import_single_manifest(man_data, remote_url):
    """Import a single manifest.

    :param man_data: Pre-fetched text of data from remote_url
    :param remote_url: Url of manifest.
    :return: ImportResult with all information about the result of this task.
    """
    man = ManifestImporter(remote_url, prefetched_data=man_data)
    errors = []
    warnings = []

    try:
        imp_success = man.create()
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

    return ImportResult(status, man.id, man.remote_url, errors, warnings)


@shared_task(ignore_results=True)
def test_manifest(man_id):
    try:
        man = Manifest.objects.get(id=man_id)
    except Manifest.DoesNotExist:
        print("Warning: Tried to test manifest '{}', but it does not exist.").format(man_id)
        return
    man.do_tests()


@after_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):
    # Change task.status to 'SENT' for all tasks which are sent in.
    # This allows one to distinguish between PENDING tasks which have been
    # sent in and tasks which do not exist. State will change to
    # SUCCESS, FAILURE, etc. once the process terminates.
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    backend.store_result(body['id'], None, "SENT")
