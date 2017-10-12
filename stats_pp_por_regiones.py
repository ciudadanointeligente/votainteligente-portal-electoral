# coding=utf-8
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "votainteligente.settings")
django.setup()
import pprint
from popular_proposal.models import PopularProposal
pp = pprint.PrettyPrinter(indent=4)

regiones = {}
for p in PopularProposal.objects.filter(generated_at__classification="Comuna"):
	region = p.generated_at.parent.parent.parent
	if region.id not in regiones.keys():
		regiones[region.id] = [p]
	else:
		regiones[region.id].append(p)

pp.pprint(regiones)