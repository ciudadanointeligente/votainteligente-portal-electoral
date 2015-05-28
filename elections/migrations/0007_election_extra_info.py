# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0006_personaldata'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='extra_info',
            field=picklefield.fields.PickledObjectField(default={}, editable=False),
        ),
    ]
