# coding=utf-8
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "votainteligente.settings")
django.setup()
import pprint
from popular_proposal.models import Commitment
from elections.models import Election
for e in Election.objects.all():
    candidatos_loggeads_no_comprometidos = []
    candidatos_loggeads_comprometidos = []
    candidatos_loggeados = 0
    for c in e.candidates.all():
        if c.has_logged_in():
            candidatos_loggeados += 1
            if c.commitments.count():
                candidatos_loggeads_comprometidos.append(c.name)
            else:
                candidatos_loggeads_no_comprometidos.append(c.name)
    print e.name + u"|" + unicode(len(candidatos_loggeads_no_comprometidos)) + u'|' + unicode(len(candidatos_loggeads_comprometidos)) + u"|" + unicode(candidatos_loggeads_no_comprometidos) + u"|" + unicode(candidatos_loggeads_comprometidos)
