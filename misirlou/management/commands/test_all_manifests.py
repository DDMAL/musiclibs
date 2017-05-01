import random

from django.core.management.base import BaseCommand

from misirlou.models import Manifest
from misirlou.models.manifest import test_if_needed


class Command (BaseCommand):
    """Test all manifests that have not been tested in a certain timeframe."""

    help = 'Test all manifests in the database that have not recently been tested.'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--days', type=int, default=14, help='Number of days since last tested. That is, '
                                                                       'manifests which have not been tested for this '
                                                                       'many days will be targeted.')

    def handle(self, *args, **options):
        manifests = list(Manifest.objects.indexed())
        random.shuffle(manifests)

        for m in manifests:
            test_if_needed(Manifest, m, days_since_last_test=options['days'])
