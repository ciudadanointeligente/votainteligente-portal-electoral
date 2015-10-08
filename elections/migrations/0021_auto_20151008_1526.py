# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0020_auto_20150821_2101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='election',
        ),
        migrations.AddField(
            model_name='candidate',
            name='election',
            field=models.ManyToManyField(related_name='candidates', null=True, to='elections.Election'),
        ),
    ]
