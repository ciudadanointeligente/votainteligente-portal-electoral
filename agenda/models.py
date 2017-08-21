from __future__ import unicode_literals

from django.db import models


class Activity(models.Model):
    date = models.DateField()
    url = models.URLField()
    location = models.CharField(max_length=1024)
    description = models.TextField(blank=True)
    updated = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now=True)
