from misirlou.models import Manifest
from collections import defaultdict
import urllib.parse
import tqdm
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command for finding duplicate manifests in the database.

    A list of duplicated manifests is returned.

    manage.py dupe_check
    """
    help = 'Check the database for duplicates.'

    def handle(self, *args, **options):
        print(find_dupes())


def find_dupes():
    """Creates a list of lists of duplicated manifests."""
    dupe_dict = defaultdict(list)
    for m in tqdm.tqdm(Manifest.objects.all()):
        parsed = urllib.parse.urlparse(m.remote_url)
        netloc_and_path = "".join(parsed[1:3])
        dupe_dict[netloc_and_path].append(m)
    return [v for v in dupe_dict.values() if len(v) > 1]
