# coding=utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from images.models import Image, HasImageMixin
from popolo.models import Organization as PopoloOrganization
from django.contrib.contenttypes.fields import GenericRelation


class Profile(models.Model):
    user = models.OneToOneField(User)
    image = models.ImageField(upload_to="users/profiles/",
                              null=True,
                              blank=True,
                              verbose_name=_('Tu imagen de perfil'))
    description = models.TextField(verbose_name=_('Tu descripción'))
    first_time_in_backend_citizen = models.BooleanField(default=False)
    is_organization = models.BooleanField(default=False)


@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_user_profile(sender, instance, created, raw, **kwargs):
    try:
        instance.profile
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)


class Organization(PopoloOrganization, HasImageMixin):
    _id = models.AutoField(primary_key=True)
    images = GenericRelation(Image)

    def get_absolute_url(self):
        return reverse('backend_citizen:organization',
                       kwargs={'slug': self.id})


class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name="enrollments")
    organization = models.ForeignKey(Organization, related_name="enrollments")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)