from tqdm import tqdm
from django.core.management.base import BaseCommand
from misirlou.models.manifest import Manifest


class Command (BaseCommand):
    """Reindex all indexed manifests locally."""

    def handle(self, *args, **kwargs):
        for manifest in tqdm(Manifest.objects.indexed()):
            manifest.re_index_from_stored()
