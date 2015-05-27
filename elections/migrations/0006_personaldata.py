# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0005_candidate_extra_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=512)),
                ('value', models.CharField(max_length=1024)),
                ('candidate', models.ForeignKey(related_name='personal_datas', to='elections.Candidate')),
            ],
        ),
    ]
