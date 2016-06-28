from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from elections.models import Candidate


class Candidacy(models.Model):
    user = models.ForeignKey(User)
    candidate = models.ForeignKey(Candidate)
    created = models.DateTimeField(auto_now_add=True,
                                   blank=True,
                                   null=True)
    updated = models.DateTimeField(auto_now=True,
                                   blank=True,
                                   null=True)

