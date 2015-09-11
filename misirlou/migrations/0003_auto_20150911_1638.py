# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('misirlou', '0002_document_remote_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='remote_URL',
            new_name='remote_url',
        ),
    ]
