from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from popolo.models import Organization


class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name="enrollments")
    organization = models.ForeignKey(Organization, related_name="enrollments")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
