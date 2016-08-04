# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-08-01 16:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('backend_candidate', '0002_auto_20160801_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidacycontact',
            name='candidacy',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend_candidate.Candidacy'),
        ),
        migrations.AddField(
            model_name='candidacycontact',
            name='identifier',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
