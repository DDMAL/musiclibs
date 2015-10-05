# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('misirlou', '0005_auto_20150916_1912'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manifest',
            name='errors',
        ),
        migrations.RemoveField(
            model_name='manifest',
            name='indexed',
        ),
    ]
