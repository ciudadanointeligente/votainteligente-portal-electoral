# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from backend_citizen.models import Profile
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from autoslug import AutoSlugField
from django.conf import settings
import markdown2


@python_2_unicode_compatible
class OrganizationTemplate(models.Model):
    organization = models.OneToOneField(User, related_name='organization_template')
    content = models.TextField(default="")
    logo = models.ImageField(upload_to="organizations/profiles/",
                              null=True,
                              blank=True,
                              verbose_name=_(u'El logo de tu organización'))
    background_image = models.ImageField(upload_to="organizations/backgrounds/",
                              null=True,
                              blank=True,
                              verbose_name=_(u'Imagen de fondo'))
    title = models.CharField(max_length=512,
                                verbose_name=_(u'Título de tu organización'),
                                blank=True,
                                null=True)
    sub_title = models.TextField(verbose_name=_('Bajada'),
                                   null=True,
                                   blank=True)
    org_url = models.URLField(blank=True,
                                null=True)
    facebook = models.URLField(blank=True,
                                null=True)
    twitter = models.URLField(blank=True,
                                null=True)
    instagram = models.URLField(blank=True,
                                null=True)
    primary_color = models.CharField(max_length=8,
                                verbose_name=_(u'Color primario'),
                                default="#CCDDCC")
    secondary_color = models.CharField(max_length=8,
                                verbose_name=_(u'Color secundario'),
                                default="#DDCCDD")
    rss_url = models.URLField(blank=True,
                                null=True)

    def __str__(self):
        return "Template for %s" % (str(self.organization))

    def create_default_extra_pages(self):
        for data in settings.DEFAULT_EXTRAPAGES_FOR_ORGANIZATIONS:
            ExtraPage.objects.create(template=self,
                                     title=data["title"],
                                     content=data["content"])


BASIC_FIELDS = ["logo", "background_image", "title", "sub_title",
                "org_url", "facebook", "twitter", "instagram", "primary_color",
                "secondary_color", "rss_url",]

class ExtraPage(models.Model):
    template = models.ForeignKey(OrganizationTemplate, related_name='extra_pages')
    content = models.TextField(default="")
    title = models.CharField(max_length=512,
                             verbose_name=_(u'Título'))
    slug = AutoSlugField(populate_from='title', unique=True)

    @property
    def content_markdown(self):
        return markdown2.markdown(self.content)

@receiver(post_save, sender=Profile, dispatch_uid="create_user_profile")
def create_organization_template(sender, instance, created, raw, **kwargs):
    if raw:
        return
    if(instance.is_organization):
        template, created = OrganizationTemplate.objects.get_or_create(organization=instance.user)
        if created:
            template.create_default_extra_pages()
