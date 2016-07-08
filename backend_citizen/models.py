# coding=utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(User)
    is_organization = models.BooleanField(default=False)
    image = models.ImageField(upload_to="users/profiles/",
                              null=True,
                              blank=True,
                              verbose_name=_('Tu imagen de perfil'))
    description = models.TextField(verbose_name=_('Tu descripción'))

@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_user_profile(sender, instance, created, raw, **kwargs):
    try:
        instance.profile
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
