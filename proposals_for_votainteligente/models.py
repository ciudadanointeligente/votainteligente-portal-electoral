# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from elections.models import Area
from votainteligente.send_mails import send_mail
from django.conf import settings


class ProposalsAdapter(models.Model):
    area = models.ForeignKey(Area, related_name="%(class)ss", null=True, blank=True)
    generated_at = models.ForeignKey(Area,
                                     related_name='%(class)ss_generated_here',
                                     null=True,
                                     blank=True)
    def notify_authorities_of_new(self):
        if not (settings.NOTIFY_CANDIDATES and settings.NOTIFY_CANDIDATES_OF_NEW_PROPOSAL):
            return
        template = 'notification_for_candidates_of_new_proposal'
        context = {'proposal': self}
        area = Area.objects.get(id=self.area.id)
        for election in area.elections.all():
            for candidate in election.candidates.all():
                for contact in candidate.contacts.all():
                    context.update({'candidate': candidate})
                    send_mail(context,
                              template,
                              to=[contact.mail])

    def get_mail_context(self):
        return {
            'area': self.area
        }

    class Meta:
        abstract = True