# coding=utf-8
from __future__ import unicode_literals
from django.db import models
from django.contrib.sites.models import Site


class CustomSite(models.Model):
    site = models.OneToOneField(Site, related_name='custom_site')
    urlconf = models.CharField(max_length=512)
