"""This script simply iterates through all manifests and tests that
they are still reachable and updates them if needed.

Good idea: set up this script with a cron-job that runs it every week.
This ensures that all the manifests in the database are tested for if
they need to be updated at least once a week.
"""

import random
from misirlou.models import Manifest
from misirlou.models.manifest import test_if_needed

manifests = Manifest.objects.indexed()
random.shuffle(manifests)

for m in manifests:
    test_if_needed(Manifest, m)
