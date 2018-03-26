# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from popular_proposal.models import PopularProposal, Commitment

class MeRepresentaPopularProposal(PopularProposal):
    class Meta:
        proxy = True


class MeRepresentaCommitment(Commitment):
    class Meta:
        proxy = True
        
    def save(self, *args, **kwargs):
        return self._save(*args, **kwargs)