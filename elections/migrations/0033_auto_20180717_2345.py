# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-17 23:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0032_auto_20180525_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name=b'PersonalData',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='personal_datas', to='elections.Candidate'),
        ),
        migrations.AlterField(
            model_name=b'CandidateFlatPage',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flatpages', to='elections.Candidate'),
        ),
        migrations.AlterField(
            model_name='election',
            name='extra_info_content',
            field=models.TextField(blank=True, help_text='Puedes usar Markdown. <br/> <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> allowed, but no raw HTML. Examples: **bold**, *italic*, indent 4 spaces for a code block.', max_length=3000, null=True),
        ),
    ]
