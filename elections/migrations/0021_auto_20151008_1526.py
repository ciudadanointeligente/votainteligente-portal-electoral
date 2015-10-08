# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def from_election_to_elections(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Election = apps.get_model("elections", "Election")
    Candidate = apps.get_model("elections", "Candidate")
    for candidate in Candidate.objects.all():
        candidate.elections.add(candidate.election)



class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0020_auto_20150821_2101'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='elections',
            field=models.ManyToManyField(related_name='candidates', null=True, to='elections.Election'),
        ),
        migrations.RunPython(from_election_to_elections),
    ]
