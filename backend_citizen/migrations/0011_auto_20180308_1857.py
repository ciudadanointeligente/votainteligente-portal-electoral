# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-08 18:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('popular_proposal', '0032_auto_20180308_1857'),
        ('popolo', '0004_auto_20180308_1857'),
        ('backend_citizen', '0010_auto_20171005_1822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enrollment',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='enrollment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='organization_ptr',
        ),
        migrations.AlterField(
            model_name='profile',
            name='unsubscribed',
            field=models.BooleanField(default=False, verbose_name='No quiero recibir noticias sobre las propuestas que me gustan'),
        ),
        migrations.DeleteModel(
            name='Enrollment',
        ),
        migrations.DeleteModel(
            name='Organization',
        ),
    ]
