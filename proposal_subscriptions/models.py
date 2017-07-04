from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from picklefield.fields import PickledObjectField
from django.utils import timezone
from django.core.urlresolvers import reverse
import uuid
from django.utils.translation import ugettext_lazy as _


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
