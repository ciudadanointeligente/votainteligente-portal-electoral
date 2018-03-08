from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from popular_proposal.models import Commitment
from picklefield.fields import PickledObjectField
from django.utils import timezone
from django.core.urlresolvers import reverse
import uuid
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from votai_utils.send_mails import send_mail


class SearchSubscription(models.Model):
    user = models.ForeignKey(User, related_name="search_subscriptions")
    keyword_args = PickledObjectField()
    search_params = PickledObjectField()
    filter_class_module = models.CharField(max_length=254)
    filter_class_name = models.CharField(max_length=254)
    oftenity = models.DurationField(help_text=_(u"Cada cuanto te notificamos?"))
    created = models.DateTimeField(auto_now_add=True,
                                   blank=True,
                                   null=True)
    updated = models.DateTimeField(auto_now=True,
                                   blank=True,
                                   null=True)
    last_run = models.DateTimeField(blank=True,
                                    null=True)
    token = models.UUIDField(default=uuid.uuid4)

    def unsubscribe_url(self):
        return reverse('proposal_subscriptions:unsubscribe', kwargs={'token': self.token})

    def base_queryset(self):
        mod = __import__(self.filter_class_module, fromlist=[self.filter_class_name])
        filter_klass = getattr(mod, self.filter_class_name)
        filter_ = filter_klass(data=self.search_params, **self.keyword_args)
        return filter_.qs

    def queryset(self):
        qs = self.base_queryset()
        since_when = timezone.now() - self.oftenity
        return qs.filter(created__gt=since_when)


class CommitmentNotification(models.Model):
    user = models.ForeignKey(User, related_name='commitment_notifications')
    commitment = models.ForeignKey(Commitment, related_name="notifications")
    notified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True,
                                   blank=True,
                                   null=True)

class CommitmentNotificationSender(object):
    template_prefix = "commitments_summary"

    def __init__(self, user):
        self.user = user

    def get_commitments(self):
        return Commitment.objects.filter(notifications__user=self.user, notifications__notified=False)

    def get_context(self):
        commitments = self.get_commitments()
        return {
            'commitments': commitments,
            'user': self.user
        }

    def send(self):
        context = self.get_context()
        if not context['commitments']:
            return
        for commitment in context['commitments']:
            commitment.notifications.filter(user=self.user).update(notified=True)
        send_mail(context, self.template_prefix, to=[self.user.email])

    @classmethod
    def send_to_users(cls):
        users = User.objects.exclude(commitment_notifications__isnull=True).exclude(profile__unsubscribed=True)
        for u in users:
            instance = cls(user=u)
            instance.send()

@receiver(post_save, sender=Commitment, dispatch_uid="create_notifications")
def create_notifications(sender, instance, created, raw, **kwargs):
    commitment = instance
    if created:
        for user in commitment.proposal.likers.all():
            CommitmentNotification.objects.get_or_create(commitment=commitment,
                                                         user=user)
