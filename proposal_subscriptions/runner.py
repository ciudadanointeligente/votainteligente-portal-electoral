# coding=utf-8
from .models import SearchSubscription
from itertools import chain


class SubscriptionRunner(object):
    def __init__(self, user):
        self.user = user
        
    def get_proposals(self):
        subscriptions = SearchSubscription.objects.filter(user=self.user)
        proposals_iter = []
       	for subscription in subscriptions:
               proposals_iter += list(subscription.queryset())
        return set(proposals_iter)