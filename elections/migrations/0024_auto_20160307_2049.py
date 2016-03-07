# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0022_remove_candidate_election'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='elections',
            field=models.ManyToManyField(default=None, related_name='candidates', null=True, to='elections.Election'),
        ),
    ]
