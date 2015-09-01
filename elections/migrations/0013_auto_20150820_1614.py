# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candidator', '0004_auto_20150714_1756'),
        ('writeit', '__first__'),
        ('elections', '0012_candidate_force_has_answer'),
    ]

    operations = [
        migrations.CreateModel(
            name='VotaInteligenteMessage',
            fields=[
                ('message_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='writeit.Message')),
                ('moderated', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            bases=('writeit.message',),
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
            ],
            options={
                'verbose_name': 'Position',
                'proxy': True,
                'verbose_name_plural': 'Positions',
            },
            bases=('candidator.position',),
        ),
        migrations.CreateModel(
            name='TakenPosition',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('candidator.takenposition',),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='force_has_answer',
            field=models.BooleanField(default=False, help_text='Marca esto si quieres que el candidato aparezca como que no ha respondido'),
        ),
    ]
