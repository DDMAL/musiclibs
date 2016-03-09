from __future__ import absolute_import

from celery import shared_task
from celery import current_app
from celery.signals import after_task_publish
from celery import group
from django.conf import settings
from .helpers.IIIFImporter import Importer, WIPManifest
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
        c = CollectionImporter(shared_id)
        return c.import_collection(lst)

    else:
        return {'error': 'Could not find manifests.', 'status': settings.ERROR}


@shared_task
def import_single_manifest(remote_url):
    man = WIPManifest(remote_url, str(uuid.uuid4()))
    this_trace = {'errors': [], 'status': settings.SUCCESS, 'rem_url': remote_url}

    try:
        imp_success = man.create(False)
    except Exception as e:
        imp_success = False
        this_trace['errors'].append(str(e))

    if not imp_success:
        this_trace['errors'].append(man.errors)
        this_trace['status'] = settings.ERROR

    return this_trace


class CollectionImporter:
    def __init__(self, shared_id):
        self.shared_id = shared_id
        self.processed = 0
        self.succeeded = 0
        self.length = 0
        self.failed = []
        self.data = {'error': {}}
        self.solr_con = scorched.SolrInterface(settings.SOLR_SERVER)

    def import_collection(self, lst):
        self.length = len(lst)
        results = group(import_single_manifest.s(rem_url) for rem_url in lst).apply_async()

        for incoming in results.iterate():

            self.processed += 1
            status = incoming['status']
            rem_url = incoming['rem_url']
            errors = incoming['errors']

            if status == settings.SUCCESS:
                self.succeeded += 1

            if incoming['errors']:
                self.data['error'][rem_url] = {'errors': errors}
                self.failed.append(rem_url)

            create_manifest.update_state(task_id=self.shared_id,
                                         state=settings.PROGRESS,
                                         meta={'current': self.processed, 'total': self.length})
        self.solr_con.commit()
        self.data['status'] = settings.SUCCESS if self.succeeded else settings.ERROR
        self.data['type'] = "collection"
        self.data['total'] = self.length
        self.data['succeeded'] = self.succeeded
        self.data['failed'] = self.failed
        return self.data

@after_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):
    # Change task.status to 'SENT' for all tasks which are sent in.
    # This allows one to distinguish between PENDING tasks which have been
    # sent in and tasks which do not exist. State will change to
    # SUCCESS, FAILURE, etc. once the process terminates.
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    backend.store_result(body['id'], None, "SENT")
