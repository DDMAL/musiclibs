from __future__ import absolute_import

from celery import shared_task
from .models.manifest import Manifest

import uuid

@shared_task
def create_manifest(remote_url, shared_id):
    manifest = Manifest(remote_url=remote_url, uuid=uuid.UUID(shared_id))
    manifest.save()
