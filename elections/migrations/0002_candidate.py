# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '__first__'),
        ('elections', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('person_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='popolo.Person')),
            ],
            options={
                'abstract': False,
            },
            bases=('popolo.person',),
        ),
    ]
