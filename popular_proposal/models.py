from __future__ import unicode_literals

from django.db import models
from picklefield.fields import PickledObjectField
from django.contrib.auth.models import User
from popolo.models import Area
from djchoices import DjangoChoices, ChoiceItem
from votainteligente.send_mails import send_mail
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
from autoslug import AutoSlugField
from django.core.urlresolvers import reverse
from backend_citizen.models import Organization
from votainteligente.open_graph import OGPMixin
from elections.models import Candidate


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
    area = models.ForeignKey(Area, related_name='temporary_proposals')
    data = PickledObjectField()
    rejected = models.BooleanField(default=False)
    rejected_reason = models.TextField(null=True,
                                       blank=True)
    organization = models.ForeignKey(Organization,
                                     related_name='temporary_proposals',
                                     null=True,
                                     blank=True,
                                     default=None)
    comments = PickledObjectField()
    status = models.CharField(max_length=16,
                              choices=Statuses.choices,
                              validators=[Statuses.validator],
                              default=Statuses.InOurSide)
    overall_comments = models.CharField(max_length=512,
                                        blank=True,
                                        null=True,
                                        default="")
    created = models.DateTimeField(auto_now_add=True,
                                   blank=True,
                                   null=True)
    updated = models.DateTimeField(auto_now=True,
                                   blank=True,
                                   null=True)

    needing_moderation = NeedingModerationManager()
    objects = models.Manager()

    def save(self, *args, **kwargs):
        creating = self.id is None
        if not self.comments:
            self.comments = {}
        for key in self.data.keys():
            if key not in self.comments.keys():
                self.comments[key] = ''
        return super(ProposalTemporaryData, self).save(*args, **kwargs)

    def notify_new(self):
        site = Site.objects.get_current()
        mail_context = {
            'area': self.area,
            'temporary_data': self,
            'site': site,
        }
        send_mail(mail_context, 'new_temporary_proposal',
                  to=[self.proposer.email])

    def create_proposal(self, moderator=None):
        self.status = ProposalTemporaryData.Statuses.Accepted
        self.save()
        title = self.get_title()
        clasification = self.data.get('clasification', '')
        popular_proposal = PopularProposal(proposer=self.proposer,
                                           title=title,
                                           area=self.area,
                                           temporary=self,
                                           clasification=clasification,
                                           data=self.data)
        if 'organization' in self.data.keys() and self.data['organization']:
            org_id = self.data['organization']
            enrollment = self.proposer.enrollments.get(organization__id=org_id)
            popular_proposal.organization = enrollment.organization
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
        send_mail(mail_context, 'popular_proposal_rejected',
                  to=[self.proposer.email])

    def get_title(self):
        return self.data.get('title', u'')

    def __str__(self):
        return self.get_title()


@python_2_unicode_compatible
class PopularProposal(models.Model, OGPMixin):
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
    organization = models.ForeignKey(Organization,
                                     related_name='popular_proposals',
                                     null=True)
    background = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='proposals/image/',
                              max_length=512,
                              null=True,
                              blank=True)
    clasification = models.CharField(blank=True, null=True, max_length=255)

    ogp_enabled = True

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('popular_proposals:detail', kwargs={'slug': self.slug})


class ProposalLike(models.Model):
    user = models.ForeignKey(User)
    proposal = models.ForeignKey(PopularProposal)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)


class Commitment(models.Model):
    proposal = models.ForeignKey(PopularProposal)
    candidate = models.ForeignKey(Candidate)
    detail = models.CharField(max_length=1024,
                              null=True,
                              blank=True)
    commited = models.BooleanField()

    def save(self, *args, **kwargs):
        instance = super(Commitment, self).save(*args, **kwargs)
        from popular_proposal.subscriptions import notification_trigger
        notification_trigger('new-commitment',
                             proposal=self.proposal,
                             commitment=self)
        return instance
