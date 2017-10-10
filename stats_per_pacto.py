# coding=utf-8
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "votainteligente.settings")
django.setup()
import pprint
from popular_proposal.models import PopularProposal
pp = pprint.PrettyPrinter(indent=4)
stats = {}
for p in PopularProposal.objects.exclude(commitments__isnull=True):
    stats[p.slug] = {}
    for c in p.commitments.all():
        if c.candidate.personal_datas.filter(label="Pacto").exists():
            if c.candidate.personal_datas.get(label="Pacto").value in stats[p.slug].keys():

                stats[p.slug][c.candidate.personal_datas.get(label="Pacto").value] += 1
            else:
                stats[p.slug][c.candidate.personal_datas.get(label="Pacto").value] = 1

pp.pprint(stats)