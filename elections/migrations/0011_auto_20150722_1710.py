# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0010_candidateflatpage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='candidate',
            options={'verbose_name': 'Candidato', 'verbose_name_plural': 'Candidatos'},
        ),
        migrations.AlterModelOptions(
            name='candidateflatpage',
            options={'verbose_name': 'P\xe1gina est\xe1ticas por candidato', 'verbose_name_plural': 'P\xe1ginas est\xe1ticas por candidato'},
        ),
        migrations.AlterModelOptions(
            name='questioncategory',
            options={'verbose_name': 'Categor\xeda de pregunta', 'verbose_name_plural': 'Categor\xedas de pregunta'},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'verbose_name': 'Pregunta', 'verbose_name_plural': 'Preguntas'},
        ),
        migrations.AlterField(
            model_name='candidateflatpage',
            name='candidate',
            field=models.ForeignKey(related_name='flatpages', to='elections.Candidate'),
        ),
    ]
