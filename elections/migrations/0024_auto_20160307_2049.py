# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0023_auto_20160224_2130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='elections',
            field=models.ManyToManyField(default=None, related_name='candidates', null=True, to='elections.Election'),
        ),
    ]
