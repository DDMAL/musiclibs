# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('misirlou', '0004_auto_20150911_1933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manifest',
            name='id',
        ),
        migrations.AddField(
            model_name='manifest',
            name='errors',
            field=models.CharField(null=True, max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='manifest',
            name='indexed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='manifest',
            name='uuid',
            field=models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4),
        ),
    ]
