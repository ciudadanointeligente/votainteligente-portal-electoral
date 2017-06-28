# coding=utf-8
from .models import SearchSubscription
from itertools import chain
from django.utils import timezone
from django.db.models import DateTimeField, ExpressionWrapper, F


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
