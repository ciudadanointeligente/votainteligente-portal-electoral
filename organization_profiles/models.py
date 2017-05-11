from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class OrganizationTemplate(models.Model):
    organization = models.ForeignKey(User)
