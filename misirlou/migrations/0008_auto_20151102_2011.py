# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('misirlou', '0007_auto_20151005_1911'),
    ]

    operations = [
        migrations.RenameField(
            model_name='manifest',
            old_name='uuid',
            new_name='id',
        ),
    ]
