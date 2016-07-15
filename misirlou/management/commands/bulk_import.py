import os
import time
import sys
import csv

from django.core.management.base import BaseCommand
from misirlou.tasks import import_single_manifest


class Command(BaseCommand):
    """Command for importing from a file. Use it like:

    manage.py bulk_import --delay=[seconds] [files to import[files]]
    """
    help = 'Import a list of urls saved in a file.'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--delay', type=float, default=0.3, help="Seconds to wait between requests.")
        parser.add_argument('file', nargs='*', help="File containing list of urls.")

    def handle(self, *args, **options):
        for file in options['file']:
            self.import_from_file(file, options['delay'])

    def import_from_file(self, path, delay):
        """Import manifests from a newline delimited file of urls."""
        if not os.path.exists(path):
            print("{} is not reachable.".format(path))
            return
        with open(path) as f:
            writer = csv.writer(sys.stdout)
            writer.writerow(('status', 'id', 'url', 'errors', 'warnings'))
            for line in f:
                line = line.strip('\n')
                res = import_single_manifest(None, line)
                writer.writerow(res)
                time.sleep(delay)
