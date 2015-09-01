# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0018_auto_20150821_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='uses_ranking',
            field=models.BooleanField(default=False, help_text='Esta elecci\xf3n debe usar ranking'),
        ),
    ]
