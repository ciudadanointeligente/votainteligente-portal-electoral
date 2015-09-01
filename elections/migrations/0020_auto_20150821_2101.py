# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0019_auto_20150821_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votainteligenteanswer',
            name='person',
            field=models.ForeignKey(related_name='answers', to='elections.Candidate'),
        ),
    ]
