# coding=utf-8
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "votainteligente.settings")
django.setup()
import pprint
from popular_proposal.models import Commitment
from elections.models import PersonalData
pp = pprint.PrettyPrinter(indent=4)
stats = {}

for p in PersonalData.objects.filter(label="Pacto").distinct("value"):
    ps = Commitment.objects.filter(candidate__personal_datas__label="Pacto", candidate__personal_datas__value=p.value).count()
    print(p.value + "|" + str(ps))
