# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '__first__'),
        ('elections', '0007_election_extra_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='area',
            field=models.ForeignKey(related_name='elections', to='popolo.Area', null=True),
        ),
    ]
