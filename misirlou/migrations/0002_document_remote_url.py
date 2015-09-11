# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('misirlou', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='remote_URL',
            field=models.TextField(default=''),
        ),
    ]
