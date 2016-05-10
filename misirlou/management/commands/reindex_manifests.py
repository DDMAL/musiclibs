from django.core.management.base import BaseCommand

from misirlou.models.manifest import Manifest


class Command (BaseCommand):
    """Reindex all manifests"""

    def handle(self, *args, **kwargs):
        for manifest in Manifest.objects.all():
            manifest.re_index()
