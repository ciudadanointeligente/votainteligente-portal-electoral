# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candidator', '__first__'),
        ('elections', '0008_election_area'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('candidator.topic',),
        ),
    ]
