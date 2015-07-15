# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0001_initial'),
        ('elections', '0009_topic'),
    ]

    operations = [
        migrations.CreateModel(
            name='CandidateFlatPage',
            fields=[
                ('flatpage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='flatpages.FlatPage')),
                ('candidate', models.ForeignKey(to='elections.Candidate')),
            ],
            bases=('flatpages.flatpage',),
        ),
    ]
