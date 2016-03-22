from __future__ import unicode_literals

from django.db import models
from picklefield.fields import PickledObjectField
from django.contrib.auth.models import User
from popolo.models import Area


class ProposalTemporaryData(models.Model):
    user = models.ForeignKey(User, related_name='temporary_proposals')
    area = models.ForeignKey(Area, related_name='temporary_proposals')
    data = PickledObjectField()
    rejected = models.BooleanField(default=False)
    rejected_reason = models.TextField()
    comments = PickledObjectField()

    def save(self, *args, **kwargs):
        self.comments = {}
        for key in self.data.keys():
            self.comments[key] = ''
        return super(ProposalTemporaryData, self).save(*args, **kwargs)
