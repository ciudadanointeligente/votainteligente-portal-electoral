from __future__ import unicode_literals

from django.db import models
from picklefield.fields import PickledObjectField
from django.contrib.auth.models import User
from popolo.models import Area, Organization
from djchoices import DjangoChoices, ChoiceItem
from votainteligente.send_mails import send_mail
from django.utils.encoding import python_2_unicode_compatible
from backend_citizen.models import Enrollment
from django.contrib.sites.models import Site
from autoslug import AutoSlugField
from django.core.urlresolvers import reverse


class NeedingModerationManager(models.Manager):
    def get_queryset(self):
        qs = super(NeedingModerationManager, self).get_queryset()
        qs = qs.filter(status=ProposalTemporaryData.Statuses.InOurSide)
        return qs


@python_2_unicode_compatible
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
    rejected_reason = models.TextField(null=True,
                                       blank=True)
    comments = PickledObjectField()
    status = models.CharField(max_length=16,
                              choices=Statuses.choices,
                              validators=[Statuses.validator],
                              default=Statuses.InOurSide)
    overall_comments = models.CharField(max_length=512,
                                        blank=True,
                                        null=True,
                                        default="")

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
        title = self.get_title()
        popular_proposal = PopularProposal(proposer=self.proposer,
                                           title=title,
                                           area=self.area,
                                           temporary=self,
                                           data=self.data)
        if 'organization' in self.data.keys() and self.data['organization']:
            organization, created = Organization.objects.get_or_create(name=self.data['organization'])
            popular_proposal.organization = organization
            Enrollment.objects.create(organization=organization,
                                      user=self.proposer)
        popular_proposal.save()
        site = Site.objects.get_current()
        mail_context = {
            'area': self.area,
            'temporary_data': self,
            'moderator': moderator,
            'site': site,
        }
        send_mail(mail_context, 'popular_proposal_accepted', to=[self.proposer.email])
        return popular_proposal

    def reject(self, reason, moderator=None):
        self.rejected_reason = reason
        self.status = ProposalTemporaryData.Statuses.Rejected
        self.save()
        site = Site.objects.get_current()
        mail_context = {
            'area': self.area,
            'temporary_data': self,
            'moderator': moderator,
            'site': site,
        }
        send_mail(mail_context, 'popular_proposal_rejected', to=[self.proposer.email])

    def get_title(self):
        return self.data.get('title', u'')

    def __str__(self):
        return self.get_title()


@python_2_unicode_compatible
class PopularProposal(models.Model):
    title = models.CharField(max_length=255, default='')
    slug = AutoSlugField(populate_from='title', unique=True)
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
    likers = models.ManyToManyField(User, through='ProposalLike')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('popular_proposals:detail', kwargs={'slug': self.slug})


class Subscription(models.Model):
    proposal_like = models.OneToOneField('ProposalLike')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)


class ProposalLike(models.Model):
    user = models.ForeignKey(User)
    proposal = models.ForeignKey(PopularProposal)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        creating = self.id is None
        instance = super(ProposalLike, self).save(*args, **kwargs)
        if creating:
            Subscription.objects.create(proposal_like=self)
        return instance


# class SubscriptionEventBase(models.Model):
#     subscription = models.ManyToManyField(Subscription, related_name='events')
#     notified = models.BooleanField(default=False)
#
#     @classmethod
#     def get_ocurred_ones(cls):
#         result = []
#         for event in cls.objects.all():
#             if event.condition():
#                 result.append(event)
#         return result
#
#     def send_notifications(self):
#         pass
#
#     def process(self):
#         self.send_notifications()
#         self.notified = True
#         self.delete()
