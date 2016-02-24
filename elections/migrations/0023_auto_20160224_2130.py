# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0022_remove_candidate_election'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='votainteligenteanswer',
            name='message',
        ),
        migrations.RemoveField(
            model_name='votainteligenteanswer',
            name='person',
        ),
        migrations.RemoveField(
            model_name='votainteligentemessage',
            name='election',
        ),
        migrations.RemoveField(
            model_name='votainteligentemessage',
            name='message_ptr',
        ),
        migrations.DeleteModel(
            name='VotaInteligenteAnswer',
        ),
        migrations.DeleteModel(
            name='VotaInteligenteMessage',
        ),
    ]
