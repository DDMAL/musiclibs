import os

from misirlou.models import Manifest
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Import a csv file into solr omr core"""
    help = "Import a csv file into the solr omr core."

    def add_arguments(self, parser):
        parser.add_argument("id", nargs=1, help="UUID of document in database"
                                                " to attach OMR data to.")
        parser.add_argument("file", nargs=1, help="CSV file containing OMR data.")

    def handle(self, *args, **options):
        path = options['file']
        pk = options['id']

        # Fail quickly with bad args.
        man = Manifest.objects.get(id=pk)
        if not os.path.exists(path):
            raise FileNotFoundError("No such file or directory: '{}'".format(path))
