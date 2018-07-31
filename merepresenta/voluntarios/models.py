# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from elections.models import Area


class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, related_name='volunteer_profile')
    area = models.ForeignKey(Area, related_name='volunteers', null=True)

    class Meta:
        db_table = "voluntarios_profile"