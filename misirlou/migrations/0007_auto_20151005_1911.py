# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('misirlou', '0006_auto_20151005_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifest',
            name='remote_url',
            field=models.TextField(),
        ),
    ]
