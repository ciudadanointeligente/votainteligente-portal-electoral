from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from elections.models import Candidate
import uuid
from votainteligente.send_mails import send_mail
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings

class Candidacy(models.Model):
    user = models.ForeignKey(User, related_name='candidacies')
    candidate = models.ForeignKey(Candidate)
    created = models.DateTimeField(auto_now_add=True,
                                   blank=True,
                                   null=True)
    updated = models.DateTimeField(auto_now=True,
                                   blank=True,
                                   null=True)


def is_candidate(user):
    if user.candidacies.count():
        return True
    return False

def send_candidate_a_candidacy_link(candidate):
    for contact in candidate.contacts.all():
        contact.send_mail_with_link()


class CandidacyContact(models.Model):
    candidate = models.ForeignKey(Candidate, related_name='contacts')
    mail = models.EmailField()
    times_email_has_been_sent = models.IntegerField(default=0)
    used_by_candidate = models.BooleanField(default=False)
    identifier = models.UUIDField(default=uuid.uuid4)
    candidacy = models.ForeignKey(Candidacy,
                                  null=True,
                                  blank=True,
                                  default=None)

    def send_mail_with_link(self):
        if self.times_email_has_been_sent >= settings.MAX_AMOUNT_OF_MAILS_TO_CANDIDATE:
            return
        send_mail({'contact': self}, 'candidates/join_us_pls', to=[self.mail],)
        self.times_email_has_been_sent += 1
        self.save()

    def get_absolute_url(self):
        site = Site.objects.get_current()
        path = reverse('backend_candidate:candidacy_user_join',
                       kwargs={'identifier': self.identifier.hex})
        return "http://%s%s" % (site.domain, path)