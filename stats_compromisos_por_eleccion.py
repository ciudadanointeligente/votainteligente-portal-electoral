# coding=utf-8
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "votainteligente.settings")
django.setup()
import pprint
from popular_proposal.models import Commitment
from elections.models import Election
for e in Election.objects.all():
    c = e.candidates.exclude(commitments__isnull=True)
    candidatos_loggeads_no_comprometidos = e.candidates.exclude(candidacy__user__last_login__isnull=True).filter(commitments__isnull=True)
    print e.name + u"|" + unicode(c.count()) + u'|' + unicode(e.candidates.exclude(candidacy__user__last_login__isnull=True).count()) + u"|" + unicode([c.name for c in candidatos_loggeads_no_comprometidos])
