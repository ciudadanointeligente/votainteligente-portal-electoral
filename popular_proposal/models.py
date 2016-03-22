from __future__ import unicode_literals

from django.db import models
from picklefield.fields import PickledObjectField
from django.contrib.auth.models import User
from popolo.models import Area, Organization


class ProposalTemporaryData(models.Model):
    proposer = models.ForeignKey(User, related_name='temporary_proposals')
    organization = models.ForeignKey(Organization,
                                     related_name='temporary_proposals',
                                     null=True,
                                     blank=True,
                                     default=None)
    area = models.ForeignKey(Area, related_name='temporary_proposals')
    data = PickledObjectField()
    rejected = models.BooleanField(default=False)
    rejected_reason = models.TextField()
    comments = PickledObjectField()

    def save(self, *args, **kwargs):
        if not self.comments:
            self.comments = {}
        for key in self.data.keys():
            if key not in self.comments.keys():
                self.comments[key] = ''

        return super(ProposalTemporaryData, self).save(*args, **kwargs)
