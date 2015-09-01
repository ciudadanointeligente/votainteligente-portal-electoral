# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0017_auto_20150820_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='uses_preguntales',
            field=models.BooleanField(default=False, help_text='Esta elecci\xf3n debe usar preguntales?'),
        ),
    ]
