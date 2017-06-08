# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from picklefield.fields import PickledObjectField
from django.contrib.auth.models import User
from djchoices import DjangoChoices, ChoiceItem
from votainteligente.send_mails import send_mail
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
from autoslug import AutoSlugField
from django.core.urlresolvers import reverse
from backend_citizen.models import Organization
from votainteligente.open_graph import OGPMixin
from elections.models import Candidate, Area
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.mail import mail_admins
from django.template.loader import get_template


class NeedingModerationManager(models.Manager):
    def get_queryset(self):
        qs = super(NeedingModerationManager, self).get_queryset()
        qs = qs.filter(status=ProposalTemporaryData.Statuses.InOurSide)
        return qs


class ProposalCreationMixin(object):
    def determine_kwargs(self, **kwargs):
            model = kwargs.pop('model_class', self.__class__)
            for f in model._meta.fields:
                if f.name in kwargs['data'].keys():
                    kwargs[f.name] = kwargs['data'].pop(f.name)
            return kwargs


@python_2_unicode_compatible
class ProposalTemporaryData(models.Model, ProposalCreationMixin):
    class Statuses(DjangoChoices):
        InOurSide = ChoiceItem('in_our_side')
        InTheirSide = ChoiceItem('in_their_side')
        Rejected = ChoiceItem('rejected')
        Accepted = ChoiceItem('accepted')
    proposer = models.ForeignKey(User, related_name='temporary_proposals')
    area = models.ForeignKey(Area, related_name='temporary_proposals', null=True, blank=True)
    join_advocacy_url = models.URLField(null=True, blank=True)
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
        if self.proposer.email:
            send_mail(mail_context, 'new_temporary_proposal',
                      to=[self.proposer.email])

    def create_proposal(self, moderator=None):
        self.status = ProposalTemporaryData.Statuses.Accepted
        self.save()
        title = self.get_title()
        clasification = self.data.get('clasification', '')
        org_id = self.data.pop('organization', None)

        creation_kwargs = self.determine_kwargs(title=title,
                                                clasification=clasification,
                                                area=self.area,
                                                proposer=self.proposer,
                                                data=self.data,
                                                temporary=self)
        popular_proposal = PopularProposal(**creation_kwargs)
        if org_id:
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

class ProposalsOrderedManager(models.Manager):
    def by_likers(self, *args, **kwargs):
        qs = self.get_queryset()
        qs = qs.annotate(num_likers=Count('likers')).order_by('-num_likers')
        return qs



@python_2_unicode_compatible
class PopularProposal(models.Model, OGPMixin):
    title = models.CharField(max_length=255, default='')
    slug = AutoSlugField(populate_from='title', unique=True)
    proposer = models.ForeignKey(User, related_name='proposals')
    area = models.ForeignKey(Area, related_name='proposals', null=True, blank=True)
    join_advocacy_url = models.URLField(null=True, blank=True)
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
    background = models.TextField(null=True, blank=True, help_text=_(u"Antecedentes sobre tu propuesta"))
    contact_details = models.TextField(null=True,
                                       blank=True,
                                       help_text=_(u'¿Cómo te puede contactar un candidato?'))
    document = models.FileField(upload_to='uploads/proposal/backgrounds/%Y/%m/%d/',
                                help_text=_(u'¿Tienes algún documento para complementar tu propuesta?'),
                                null=True,
                                blank=True)
    image = models.ImageField(upload_to='proposals/image/',
                              max_length=512,
                              null=True,
                              blank=True)
    clasification = models.CharField(blank=True, null=True, max_length=255)
    for_all_areas = models.BooleanField(default=False)
    generated_at = models.ForeignKey(Area,
                                     related_name='proposals_generated_here',
                                     null=True,
                                     blank=True)
    is_local_meeting = models.BooleanField(default=False)

    ogp_enabled = True

    ordered = ProposalsOrderedManager()
    objects = models.Manager()

    class Meta:
        ordering = ['for_all_areas', '-created']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('popular_proposals:detail', kwargs={'slug': self.slug})

    @property
    def card(self):
        return get_template("popular_proposal/popular_proposal_card.html").render({
            'proposal': self
        })

    @property
    def sponsoring_orgs(self):
        return self.likers.filter(profile__is_organization=True)

    def notify_candidates_of_new(self):
        if not (settings.NOTIFY_CANDIDATES and settings.NOTIFY_CANDIDATES_OF_NEW_PROPOSAL):
            return
        template = 'notification_for_candidates_of_new_proposal'
        context = {'proposal': self}
        area = Area.objects.get(id=self.area.id)
        for election in area.elections.all():
            for candidate in election.candidates.all():
                for contact in candidate.contacts.all():
                    context.update({'candidate': candidate})
                    send_mail(context,
                              template,
                              to=[contact.mail])

class ProposalLike(models.Model):
    user = models.ForeignKey(User)
    proposal = models.ForeignKey(PopularProposal)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(ProposalLike, self).save(*args, **kwargs)
        created = self.pk is not None
        if created:
            if self.user.profile.is_organization:
                template = 'new_sponsorshipnotification'
                context = {'like': self}
                send_mail(context,
                          template,
                          to=[self.user.email,
                              self.proposal.proposer.email])
            self.numerical_notification()

    def numerical_notification(self):
        the_number = ProposalLike.objects.filter(proposal=self.proposal).count()
        if the_number in settings.WHEN_TO_NOTIFY:
            from popular_proposal.subscriptions import YouAreAHeroNotification, ManyCitizensSupportingNotification
            notifier = YouAreAHeroNotification(proposal=self.proposal,
                                               number=the_number)
            notifier.notify()
            notifier = ManyCitizensSupportingNotification(proposal=self.proposal,
                                                          number=the_number)
            notifier.notify()


class Commitment(models.Model):
    proposal = models.ForeignKey(PopularProposal,
                                 related_name='commitments')
    candidate = models.ForeignKey(Candidate,
                                  related_name='commitments')
    detail = models.CharField(max_length=12288,
                              null=True,
                              blank=True)
    commited = models.NullBooleanField(default=None)

    def save(self, *args, **kwargs):
        instance = super(Commitment, self).save(*args, **kwargs)
        from popular_proposal.subscriptions import notification_trigger
        notification_trigger('new-commitment',
                             proposal=self.proposal,
                             commitment=self)
        return instance

    def get_absolute_url(self):
        url = reverse('popular_proposals:commitment', kwargs={'candidate_slug': self.candidate.id,
                                                              'proposal_slug': self.proposal.slug})
        return url
