# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('preguntales', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageConfirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(default=uuid.uuid4, max_length=255)),
                ('when_confirmed', models.DateTimeField(default=None, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('message', models.OneToOneField(related_name='confirmation', to='preguntales.Message')),
            ],
        ),
    ]
