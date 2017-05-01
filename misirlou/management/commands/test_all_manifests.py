import random

from django.core.management.base import BaseCommand

from misirlou.models import Manifest
from misirlou.models.manifest import test_if_needed


class Command (BaseCommand):
    """Test all manifests that have not been tested in a certain timeframe."""

    def handle(self, *args, **kwargs):
        manifests = list(Manifest.objects.indexed())
        random.shuffle(manifests)

        for m in manifests:
            test_if_needed(Manifest, m, days_since_last_test=14)
