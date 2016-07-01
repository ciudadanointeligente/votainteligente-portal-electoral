from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from elections.models import Candidate


class Candidacy(models.Model):
    user = models.ForeignKey(User, related_name='candidacies')
    candidate = models.ForeignKey(Candidate)
    created = models.DateTimeField(auto_now_add=True,
                                   blank=True,
                                   null=True)
    updated = models.DateTimeField(auto_now=True,
                                   blank=True,
                                   null=True)


def is_candidate(user):
    if user.candidacies.count():
        return True
    return False
