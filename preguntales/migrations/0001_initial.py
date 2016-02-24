# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0023_auto_20160224_2130'),
        ('writeit', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message', models.OneToOneField(related_name='preguntales_message_related', primary_key=True, serialize=False, to='writeit.Message')),
                ('moderated', models.NullBooleanField(default=None)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('election', models.ForeignKey(related_name='messages_', default=None, to='elections.Election')),
            ],
            options={
                'verbose_name': 'Mensaje de preguntales',
                'verbose_name_plural': 'Mensajes de preguntales',
            },
            bases=('writeit.message',),
        ),
        migrations.AddField(
            model_name='answer',
            name='message',
            field=models.ForeignKey(related_name='answers_', to='preguntales.Message'),
        ),
        migrations.AddField(
            model_name='answer',
            name='person',
            field=models.ForeignKey(related_name='answers_', to='elections.Candidate'),
        ),
    ]
