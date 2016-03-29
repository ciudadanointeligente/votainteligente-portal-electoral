from __future__ import unicode_literals

from django.db import models
from picklefield.fields import PickledObjectField
from django.contrib.auth.models import User
from popolo.models import Area, Organization
from djchoices import DjangoChoices, ChoiceItem


class NeedingModerationManager(models.Manager):
    def get_queryset(self):
        qs = super(NeedingModerationManager, self).get_queryset()
        qs = qs.filter(status=ProposalTemporaryData.Statuses.InOurSide)
        print qs
        return qs


class ProposalTemporaryData(models.Model):
    class Statuses(DjangoChoices):
        InOurSide = ChoiceItem('in_our_side')
        InTheirSide = ChoiceItem('in_their_side')
        Rejected = ChoiceItem('rejected')
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
    status = models.CharField(max_length=16,
                              choices=Statuses.choices,
                              validators=[Statuses.validator],
                              default=Statuses.InOurSide)

    needing_moderation = NeedingModerationManager()
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.comments:
            self.comments = {}
        for key in self.data.keys():
            if key not in self.comments.keys():
                self.comments[key] = ''

        return super(ProposalTemporaryData, self).save(*args, **kwargs)
