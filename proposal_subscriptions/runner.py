# coding=utf-8
from .models import SearchSubscription
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import DateTimeField, ExpressionWrapper, F
from votai_utils.send_mails import send_mail


class SubscriptionRunner(object):
    def __init__(self, user):
        self.user = user

    def get_proposals(self):
        subscriptions = self.get_subscriptions()
        proposals_iter = []
        for subscription in subscriptions:
            proposals_iter += list(subscription.queryset())
        return set(proposals_iter)

    def get_subscriptions(self):
        now = timezone.now()
        subscriptions = SearchSubscription.objects.filter(user=self.user)
        subscriptions = subscriptions.annotate(should_run=ExpressionWrapper(now - F('oftenity'),
                                                                            output_field=DateTimeField()))
        subscriptions = subscriptions.exclude(created__gt=F("should_run"))
        subscriptions = subscriptions.exclude(last_run__gt=F("should_run"))
        return subscriptions

    def send(self):
        proposals = self.get_proposals()
        subscriptions = self.get_subscriptions()
        if not proposals:
            return False
        context = {'proposals': proposals,
                   'subscriptions': subscriptions,
                   'user': self.user}
        send_mail(context, 'search_proposals_subscription',
                  to=[self.user.email])
        return True


class TaskRunner(object):
    def users(self):
        return User.objects.exclude(search_subscriptions__isnull=True)

    def send(self):
        users = self.users()
        for user in users:
            runner = SubscriptionRunner(user)
            runner.send()
