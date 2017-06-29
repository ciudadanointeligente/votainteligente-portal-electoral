from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from picklefield.fields import PickledObjectField
from popular_proposal.models import PopularProposal
from django.utils import timezone


class SearchSubscription(models.Model):
    user = models.ForeignKey(User, related_name="search_subscriptions")
    keyword_args = PickledObjectField()
    search_params = PickledObjectField()
    filter_class_module = models.CharField(max_length=254)
    filter_class_name = models.CharField(max_length=254)
    oftenity = models.DurationField()
    created = models.DateTimeField(auto_now_add=True,
                                   blank=True,
                                   null=True)
    updated = models.DateTimeField(auto_now=True,
                                   blank=True,
                                   null=True)
    last_run = models.DateTimeField(blank=True,
                                    null=True)

    def base_queryset(self):
        mod = __import__(self.filter_class_module, fromlist=[self.filter_class_name])
        filter_klass = getattr(mod, self.filter_class_name)
        filter_ = filter_klass(data=self.search_params, **self.keyword_args)
        return filter_.qs

    def queryset(self):
        qs = self.base_queryset()
        since_when = timezone.now() - self.oftenity
        return qs.filter(created__gt=since_when)
