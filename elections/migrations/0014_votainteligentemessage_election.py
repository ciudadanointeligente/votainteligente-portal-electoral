# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0013_auto_20150820_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='votainteligentemessage',
            name='election',
            field=models.ForeignKey(related_name='messages', default=None, to='elections.Election'),
        ),
    ]
