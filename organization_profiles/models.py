from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from backend_citizen.models import Profile
from django.dispatch import receiver
from django.db.models.signals import post_save


class OrganizationTemplate(models.Model):
    organization = models.OneToOneField(User, related_name='organization_template')
    content = models.TextField(default="FieraFeroz")


@receiver(post_save, sender=Profile, dispatch_uid="create_user_profile")
def create_organization_template(sender, instance, created, raw, **kwargs):
    if raw:
        return
    if(instance.is_organization):
        template, created = OrganizationTemplate.objects.get_or_create(organization=instance.user)
