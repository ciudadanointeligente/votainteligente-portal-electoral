# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0014_votainteligentemessage_election'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='votainteligentemessage',
            options={'verbose_name': 'Mensaje de preguntales', 'verbose_name_plural': 'Mensajes de preguntales'},
        ),
        migrations.AlterField(
            model_name='election',
            name='slug',
            field=autoslug.fields.AutoSlugField(populate_from=b'name', unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='votainteligentemessage',
            name='moderated',
            field=models.NullBooleanField(default=None),
        ),
    ]
