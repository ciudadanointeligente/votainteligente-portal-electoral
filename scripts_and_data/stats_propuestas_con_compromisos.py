# coding=utf-8
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "votainteligente.settings")
django.setup()
import pprint
from popular_proposal.models import PopularProposal
from elections.models import Election
for p in PopularProposal.objects.exclude(commitments__isnull=True):
    c = p.commitments.count()
    print(unicode(p.id) + u"|" +p.get_classification()+ u"|" + p.title + u"|" + unicode(c))
