# coding=utf-8
from __future__ import unicode_literals
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone


class FutureActivities(models.Manager):
    def get_queryset(self):
        qs = super(FutureActivities, self).get_queryset()
        now = timezone.now()
        qs = qs.filter(date__gte=now)
        return qs

@python_2_unicode_compatible
class Activity(models.Model):
    date = models.DateTimeField()
    url = models.URLField(blank=True, null=True)
    location = models.TextField(blank=True)
    description = models.CharField(blank=True,max_length=1024)
    long_description = models.TextField(blank=True)
    contact_info = models.TextField(verbose_name=_(u'Cómo te pueden contactar las personas interesadas?'),
                                    help_text=_(u'Aquí puedes escribir un número telefónico, un email o un whatsapp.'))
    important = models.BooleanField(default=False, verbose_name=_(u'Es este evento importante?'))
    background_image = models.ImageField(upload_to="agenda/activities/",
                                        null=True,
                                        blank=True,
                                        verbose_name=_(u'Una imagen para el evento'),
                                        help_text=_(u'será la imagen que utilicemos en la lista de eventos'))
    updated = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     blank=True,
                                     null=True)
    object_id = models.CharField(max_length=1024,blank=True,
                                            null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    futures = FutureActivities()
    objects = models.Manager()

    def __str__(self):
        return self.description

    class Meta:
        # sort by "the date" in descending order unless
        # overridden in the query with order_by()
        ordering = ['date']
