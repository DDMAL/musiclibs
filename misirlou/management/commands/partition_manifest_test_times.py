import random
import math
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from misirlou.models.manifest import Manifest


class Command (BaseCommand):
    """Partitions the 'last-tested' time of all the manifests over the last 14 days.

     Shuffle the manifests and partition these shuffled manifests into 1 of the 14
     days in the last two weeks, setting the last_tested time to this day.

     Idea is that if none of the manifests have been tested in a long time, you can
     divide them up, then using `test_all_manifests -d 14`, we can test 1/14 of them each
     day for the next two weeks. Thus avoiding testing all the manifests from one provider
     on the same day."""

    _two_weeks_in_days = 14

    def handle(self, *args, **kwargs):
        m = list(Manifest.objects.all())
        random.shuffle(m)
        partition_size = math.ceil(len(m) / self._two_weeks_in_days)

        slice_left = 0
        slice_right = partition_size
        partitions = []
        for day in range(self._two_weeks_in_days):
            partitions.append(m[slice_left: slice_right])
            slice_left += partition_size
            slice_right += partition_size

        for day in range(self._two_weeks_in_days):
            target_date = timezone.now() - timedelta(day)
            for manifest in partitions[day]:
                manifest.last_tested = target_date
                manifest.save()
