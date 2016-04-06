from __future__ import unicode_literals

from django.db import models
from picklefield.fields import PickledObjectField
from django.contrib.auth.models import User
from popolo.models import Area, Organization
from djchoices import DjangoChoices, ChoiceItem
from votainteligente.send_mails import send_mail


class NeedingModerationManager(models.Manager):
    def get_queryset(self):
        qs = super(NeedingModerationManager, self).get_queryset()
        qs = qs.filter(status=ProposalTemporaryData.Statuses.InOurSide)
        return qs


class ProposalTemporaryData(models.Model):
    class Statuses(DjangoChoices):
        InOurSide = ChoiceItem('in_our_side')
        InTheirSide = ChoiceItem('in_their_side')
        Rejected = ChoiceItem('rejected')
        Accepted = ChoiceItem('accepted')
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

    def create_proposal(self, moderator=None):
        self.status = ProposalTemporaryData.Statuses.Accepted
        self.save()
        popular_proposal = PopularProposal(proposer=self.proposer,
                                           area=self.area,
                                           temporary=self,
                                           data=self.data)

        popular_proposal.save()
        mail_context = {
            'area': self.area,
            'temporary_data': self,
            'moderator': moderator,
        }
        send_mail(mail_context, 'popular_proposal_accepted', to=[self.proposer.email])
        return popular_proposal

    def reject(self, reason, moderator=None):
        self.rejected_reason = reason
        self.status = ProposalTemporaryData.Statuses.Rejected
        self.save()
        mail_context = {
            'area': self.area,
            'temporary_data': self,
            'moderator': moderator,
        }
        send_mail(mail_context, 'popular_proposal_accepted', to=[self.proposer.email])


class PopularProposal(models.Model):
    proposer = models.ForeignKey(User, related_name='proposals')
    area = models.ForeignKey(Area, related_name='proposals')
    data = PickledObjectField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    temporary = models.OneToOneField(ProposalTemporaryData,
                                     related_name='created_proposal',
                                     blank=True,
                                     null=True,
                                     default=None)
