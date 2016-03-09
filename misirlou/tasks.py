from __future__ import absolute_import

from celery import shared_task
from celery import current_app
from celery.signals import after_task_publish
from django.conf import settings
from .helpers.IIIFImporter import Importer, WIPManifest
from rest_framework.reverse import reverse
import scorched
import uuid

@shared_task
def create_manifest(remote_url, shared_id, commit=True):
    """Validate, index, and create a database entry for manifests.

    :param remote_url: A manifest or collection url.
    :param shared_id:  The UUID to be assigned to the manifest.
    """

    imp = Importer(remote_url)
    lst = imp.get_all_urls()

    if not lst:
        return {'error': 'Could not find manifests.', 'status': settings.ERROR}
    elif len(lst) == 1:
        man = WIPManifest(lst[0], shared_id)
        if man.create(commit) is False:
            create_manifest.update_state(state='ERROR')
            return {'error': man.errors,
                    'status': settings.ERROR}
        else:
            data = {'status': settings.SUCCESS, 'id': man.id}
            if man.warnings['validation'] or len(man.warnings.keys()) > 1:
                data['warnings'] = man.warnings
            if man.errors['validation'] or len(man.errors.keys()) > 1:
                data['errors'] = man.errors
            data['type'] = "manifest"
            return data
    elif len(lst) > 1:
        return _create_collection(lst)

    else:
        return {'error': 'Could not find manifests.', 'status': settings.ERROR}


def _create_collection(lst):
    length = len(lst)
    succeeded = 0
    failed = []
    data = {'trace': {}}
    solr_con = scorched.SolrInterface(settings.SOLR_SERVER)
    for i, rem_url in enumerate(lst):
        man = WIPManifest(rem_url, str(uuid.uuid4()))
        if not man.create(False):
            data['trace'][rem_url] = {}
            if man.warnings['validation'] or len(man.warnings) > 1:
                data['trace'][rem_url]['warnings'] = man.warnings
            if man.errors['validation'] or len(man.errors) > 1:
                data['trace'][rem_url]['errors'] = man.errors
            data['trace'][rem_url]['status'] = settings.ERROR
            failed.append(rem_url)
        else:
            if man.warnings['validation'] or len(man.warnings) > 1:
                data['trace'][rem_url] = {}
                data['trace'][rem_url]['warnings'] = man.warnings
            data['trace'][rem_url]['status'] = settings.SUCCESS
            data['trace'][rem_url]['location'] = reverse('manifest-detail', args=[man.id])
            succeeded += 1
        if i % 10 == 0:
            solr_con.commit()
        create_manifest.update_state(state=settings.PROGRESS,
                                     meta={'current': i, 'total': length})
    solr_con.commit()
    data['status'] = settings.SUCCESS if succeeded else settings.ERROR
    data['type'] = "collection"
    data['total'] = length
    data['succeeded'] = succeeded
    data['failed'] = failed
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
