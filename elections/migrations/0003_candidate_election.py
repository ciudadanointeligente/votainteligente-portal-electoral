# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0002_candidate'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='election',
            field=models.ForeignKey(related_name='candidates', to='elections.Election', null=True),
        ),
    ]
