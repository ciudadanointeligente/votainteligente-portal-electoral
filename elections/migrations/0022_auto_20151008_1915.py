# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0021_auto_20151008_1526'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='election',
            new_name='elections',
        ),
    ]
