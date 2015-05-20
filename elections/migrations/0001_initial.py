# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('popolo', '__first__'),
        ('candideitorg', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CandidatePerson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reachable', models.BooleanField(default=False)),
                ('description', models.TextField(default=b'', blank=True)),
                ('portrait_photo', models.CharField(max_length=256, null=True, blank=True)),
                ('custom_ribbon', models.CharField(max_length=18, null=True, blank=True)),
                ('candidate', models.OneToOneField(related_name='relation', to='candideitorg.Candidate')),
                ('person', models.OneToOneField(related_name='relation', to='popolo.Person')),
            ],
            options={
                'verbose_name': 'Extra Info de candidato',
                'verbose_name_plural': 'Extra Info de candidatos',
            },
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', autoslug.fields.AutoSlugField(unique=True, editable=False)),
                ('description', models.TextField(blank=True)),
                ('searchable', models.BooleanField(default=True)),
                ('highlighted', models.BooleanField(default=False)),
                ('extra_info_title', models.CharField(max_length=50, null=True, blank=True)),
                ('extra_info_content', models.TextField(help_text='Puedes usar Markdown. <br/> <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> allowed, but no raw HTML. Examples: **bold**, *italic*, indent 4 spaces for a code block.', max_length=3000, null=True, blank=True)),
                ('uses_preguntales', models.BooleanField(default=True, help_text='Esta elecci\xf3n debe usar preguntales?')),
                ('uses_ranking', models.BooleanField(default=True, help_text='Esta elecci\xf3n debe usar ranking')),
                ('uses_face_to_face', models.BooleanField(default=True, help_text='Esta elecci\xf3n debe usar frente a frente')),
                ('uses_soul_mate', models.BooleanField(default=True, help_text='Esta elecci\xf3n debe usar 1/2 naranja')),
                ('uses_questionary', models.BooleanField(default=True, help_text='Esta elecci\xf3n debe usar cuestionario')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Mi Elecci\xf3n',
                'verbose_name_plural': 'Mis Elecciones',
            },
        ),
    ]
