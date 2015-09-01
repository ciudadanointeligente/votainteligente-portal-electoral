# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0016_votainteligenteanswer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votainteligenteanswer',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
