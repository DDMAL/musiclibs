from __future__ import absolute_import

from celery import shared_task
from .models.manifest import Manifest

@shared_task
def create_manifest(remote_url):
    manifest = Manifest(remote_url=remote_url)
    manifest.save()
