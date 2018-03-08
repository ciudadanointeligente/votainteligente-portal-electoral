# coding=utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from images.models import Image, HasImageMixin
from django.contrib.contenttypes.fields import GenericRelation
from backend_candidate.models import unite_with_candidate_if_corresponds
import uuid


class Profile(models.Model):
    user = models.OneToOneField(User)
    image = models.ImageField(upload_to="users/profiles/",
                              null=True,
                              blank=True,
                              verbose_name=_('Tu imagen de perfil'))
    description = models.TextField(verbose_name=_('Tu descripción'),
                                   null=True,
                                   blank=True)
    first_time_in_backend_citizen = models.BooleanField(default=False)
    is_organization = models.BooleanField(default=False)
    is_journalist = models.BooleanField(default=False)
    unsubscribed = models.BooleanField(default=False,
                                       verbose_name= _(u'No quiero recibir noticias sobre las propuestas que me gustan'))
    unsubscribe_token = models.UUIDField(default=uuid.uuid4)

    def get_unsubscribe_url(self):
        return reverse('backend_citizen:unsuscribe',
                      kwargs={'token': self.unsubscribe_token})


@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_user_profile(sender, instance, created, raw, **kwargs):
    if raw:
        return
    try:
        instance.profile
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
        unite_with_candidate_if_corresponds(instance)
