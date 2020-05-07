# coding=utf-8
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "votainteligente.settings")
django.setup()
import pprint
from popular_proposal.models import PopularProposal
from elections.models import PersonalData
pp = pprint.PrettyPrinter(indent=4)
stats = {}

for p in PersonalData.objects.filter(label="Pacto").distinct("value"):
    ps = PopularProposal.objects.filter(commitments__candidate__personal_datas__label="Pacto", commitments__candidate__personal_datas__value=p.value).distinct()
    stats[p.value] = [proposal.title for proposal in ps ]
    for proposal in ps:
    	print(p.value + "|" + proposal.title)
