# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-03 14:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('misirlou', '0009_manifest_manifest_hash'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='manifest',
            options={'ordering': ('-created',)},
        ),
        migrations.AddField(
            model_name='manifest',
            name='is_valid',
            field=models.BooleanField(default=True),
        ),
    ]