# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('misirlou', '0008_auto_20151102_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='manifest',
            name='manifest_hash',
            field=models.CharField(default='', max_length=40),
        ),
    ]
