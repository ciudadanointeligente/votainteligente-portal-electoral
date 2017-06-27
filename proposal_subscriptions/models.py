from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from picklefield.fields import PickledObjectField


class SearchSubscription(models.Model):
    user = models.ForeignKey(User)
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