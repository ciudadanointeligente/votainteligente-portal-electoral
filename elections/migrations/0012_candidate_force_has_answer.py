# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0011_auto_20150722_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='force_has_answer',
            field=models.BooleanField(default=False),
        ),
    ]
