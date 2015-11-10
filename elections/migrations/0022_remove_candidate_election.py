# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0021_auto_20151008_1526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='election',
        ),
    ]
