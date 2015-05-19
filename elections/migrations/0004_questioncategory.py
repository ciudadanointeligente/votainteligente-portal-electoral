# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candidator', '__first__'),
        ('elections', '0003_candidate_election'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionCategory',
            fields=[
                ('category_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='candidator.Category')),
                ('election', models.ForeignKey(related_name='categories', to='elections.Election', null=True)),
            ],
            bases=('candidator.category',),
        ),
    ]
