# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0024_auto_20160307_2049'),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author_name', models.CharField(default=b'', max_length=256)),
                ('author_email', models.EmailField(default=b'', max_length=512)),
                ('content', models.TextField(default=b'')),
                ('subject', models.CharField(max_length=255)),
                ('slug', autoslug.fields.AutoSlugField(populate_from=b'subject', unique=True, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('election', models.ForeignKey(related_name='messages_', default=None, to='elections.Election')),
                ('people', models.ManyToManyField(to='elections.Candidate')),
            ],
            options={
                'verbose_name': 'Mensaje de preguntales',
                'verbose_name_plural': 'Mensajes de preguntales',
            },
        ),
        migrations.CreateModel(
            name='MessageStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accepted', models.NullBooleanField(default=None)),
                ('sent', models.BooleanField(default=False)),
                ('confirmed', models.NullBooleanField(default=None)),
                ('message', models.OneToOneField(related_name='status', to='preguntales.Message')),
            ],
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
