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
    elif lst:
        c = CollectionImporter(shared_id)
        return c.import_collection(lst)
    else:
        return {'error': 'Could not find manifests.', 'status': settings.ERROR}


@shared_task
def import_single_manifest(remote_url):
    man = WIPManifest(remote_url, str(uuid.uuid4()))
    this_trace = {'errors': {}, 'status': settings.SUCCESS, 'rem_url': remote_url}

    try:
        imp_success = man.create(False)
    except Exception as e:
        imp_success = False
        this_trace['errors']['server'] = str(e)

    if imp_success:
        this_trace['status'] = settings.SUCCESS
    else:
        this_trace['errors']['import'] = man.errors
        this_trace['status'] = settings.ERROR

    this_trace['man_id'] = man.id

    return this_trace


class CollectionImporter:
    def __init__(self, shared_id):
        self.shared_id = shared_id
        self.processed = 0
        self.length = 0
        self.failed_count = 0
        self.succeeded_count = 0
        self.data = {'failed': {}, 'succeeded': {}}
        self.solr_con = scorched.SolrInterface(settings.SOLR_SERVER)

    def import_collection(self, lst):
        self.length = len(lst)
        results = group(import_single_manifest.s(rem_url) for rem_url in lst).apply_async()

        for incoming in results.iterate():

            self.processed += 1
            status = incoming.get('status')
            rem_url = incoming.get('rem_url')
            errors = incoming.get('errors')
            tmp_id = incoming.get('man_id')

            if status == settings.SUCCESS:
                self.succeeded_count += 1
                self.data['succeeded'][rem_url] = {'status': status, 'uuid': tmp_id, 'url': '/manifests/{}'.format(tmp_id)}

            if incoming['errors']:
                self.failed_count += 1
                self.data['failed'][rem_url] = {'errors': errors, 'status': status, 'uuid': tmp_id}

            create_manifest.update_state(task_id=self.shared_id,
                                         state=settings.PROGRESS,
                                         meta={'current': self.processed, 'total': self.length})
        self.solr_con.commit()
        self.data['status'] = settings.SUCCESS if self.succeeded_count else settings.ERROR
        self.data['total_count'] = self.length
        self.data['succeeded_count'] = self.succeeded_count
        self.data['failed_count'] = self.failed_count
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
