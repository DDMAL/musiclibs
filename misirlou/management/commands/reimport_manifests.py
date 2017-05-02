import time

from django.core.management.base import BaseCommand

from misirlou.models.manifest import Manifest
from misirlou.helpers.manifest_utils.errors import ErrorMap
from misirlou.helpers.manifest_utils.importer import ManifestImporter
from misirlou.tasks import import_single_manifest

class Command (BaseCommand):
    """Reindex all indexed manifests locally."""

    help = 'Re-import manifests that have some error or warning on them'

    def add_arguments(self, parser):
        parser.add_argument('-e', '--error', type=str, default='', help='Code of the error to target.')
        parser.add_argument('-w', '--warning', type=str, default='', help='Code of the warning to target.')

    def handle(self, *args, **options):
        if options['error'] == '' and options['warning'] == '':
            print('Must supply either a warning or error argument (check help).')
            return
        errcode = options['warning'] if options['error'] == '' else options['error']
        errmap = ErrorMap()

        if errcode.isdigit():
            errcode = int(errcode)

        if errcode not in errmap:
            print('Unrecognized error code "{}"'.format(errcode))

        code, shortmsg, msg = errmap[errcode]

        print('Re-importing all manifests with error "{}"'.format(shortmsg))
        for manifest in Manifest.objects.with_error(code):
            import_single_manifest.delay(None, manifest.remote_url)

