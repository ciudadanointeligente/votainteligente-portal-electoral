# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from backend_citizen.models import Profile
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.core.urlresolvers import reverse
from django.db.models import Count
from autoslug import AutoSlugField
from django.conf import settings
import markdown2
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from PIL import Image, ImageDraw, ImageFont
from django.contrib.sites.models import Site
import textwrap

LOGO_SIZE = 154

class OrganizationTemplateManager(models.Manager):
    def get_queryset(self):
        qs = super(OrganizationTemplateManager, self).get_queryset()
        qs = qs.annotate(num_proposals=Count('organization__proposals')).annotate(num_likes=Count('organization__likes')).order_by("-num_proposals", "-num_likes")
        return qs

    def only_with_logos(self, *args, **kwargs):
        qs = self.get_queryset(*args, **kwargs)
        return qs.exclude(logo__isnull=True).exclude(logo__iexact='')


@python_2_unicode_compatible
class OrganizationTemplate(models.Model):
    organization = models.OneToOneField(User, related_name='organization_template')
    content = models.TextField(default="")
    logo = models.ImageField(upload_to="organizations/profiles/",
                             null=True,
                             blank=True,
                             verbose_name=_(u'El logo de tu organización'),
                             help_text=_(u'perrito'))
    logo_small = models.ImageField(upload_to="organizations/profiles_small/",
                                   null=True,
                                   blank=True)
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
                                       default="#2DDC22")
    rss_url = models.URLField(blank=True,
                              null=True)

    objects = OrganizationTemplateManager()

    def save(self, *args, **kwargs):
        super(OrganizationTemplate, self).save(*args, **kwargs)
        self.organization.profile.image = self.logo
        self.organization.profile.save()

    def __str__(self):
        return "Template for %s" % (str(self.organization))

    def generate_logo_small(self):
        if self.logo:
            im = Image.open(self.logo).convert('RGB')
            output = BytesIO()
            im = im.resize( (LOGO_SIZE,LOGO_SIZE), Image.ANTIALIAS )
            im.save(output, format='JPEG', quality=100)
            output.seek(0)
            self.logo_small = InMemoryUploadedFile(output,
                                                   'ImageField',
                                                   "%s.jpg" %self.logo.name.split('.')[0],
                                                   'image/jpeg', sys.getsizeof(output), None)
            self.save()

    def create_default_extra_pages(self):
        for data in settings.DEFAULT_EXTRAPAGES_FOR_ORGANIZATIONS:
            ExtraPage.objects.create(template=self,
                                     title=data["title"],
                                     content=data["content"])

    def get_absolute_url(self):
        return reverse('organization_profiles:home', kwargs={'slug': self.organization.username})

    def get_shared_image(self):
        plantilla = Image.open('votai_general_theme/static/img/plantilla_org.png')

        montserrat_n_propuesta = ImageFont.truetype("votai_general_theme/static/fonts/Montserrat-Bold.ttf", 16)
        arvo_titulo = ImageFont.truetype("votai_general_theme/static/fonts/Arvo-Bold.ttf", 60)
        montserrat_autor = ImageFont.truetype("votai_general_theme/static/fonts/Montserrat-Bold.ttf", 22)
        bg_color = self.primary_color
        output = BytesIO()
        output.seek(0)
        h = bg_color.lstrip('#')
        rgb_color = tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
        rgb_color = rgb_color+(0,)
        base = Image.new('RGBA',(1200,630),rgb_color)
        if self.background_image:
            bg_image = Image.open(self.background_image)
            bg_image.thumbnail((1200,1200), Image.ANTIALIAS)
            base.paste(bg_image,(0,0))
        if self.logo:
            logo = Image.open(self.logo)
            logo = logo.copy().convert('RGBA')
            base.paste(logo,(0,0))
        base.paste(plantilla, (0,0), plantilla)
        txt = Image.new('RGBA', base.size, (122,183,255,0))

        d = ImageDraw.Draw(txt)

        lines = textwrap.wrap(self.title, width=30)
        max_lines = 5
        if len(lines) > max_lines:
            last_line = lines[max_lines - 1] + u'...'
            lines = lines[0:max_lines]
            lines[max_lines - 1] = last_line

        title = '\n'.join(lines)

        d.multiline_text((81,133), title, font=arvo_titulo, fill=(rgb_color[0],rgb_color[1],rgb_color[2],255))

        out = Image.alpha_composite(base, txt)
        return out

    def ogp_image(self):
        site = Site.objects.get_current()
        image_url = reverse('organization_profiles:og_image',
                            kwargs={'slug': self.organization.username})
        url = "http://%s%s" % (site.domain,
                               image_url)
        return url


BASIC_FIELDS = ["logo", "background_image", "title", "sub_title",
                "org_url", "facebook", "twitter", "instagram", "primary_color",
                "secondary_color", "logo_small"]


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
            template.title = instance.user.get_full_name()
            template.save()
            template.create_default_extra_pages()
