# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '__first__'),
        ('elections', '0015_auto_20150820_2218'),
    ]

    operations = [
        migrations.CreateModel(
            name='VotaInteligenteAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('created', models.DateTimeField(editable=False)),
                ('message', models.ForeignKey(related_name='answers', to='elections.VotaInteligenteMessage')),
                ('person', models.ForeignKey(related_name='answers', to='popolo.Person')),
            ],
        ),
    ]
