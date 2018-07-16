# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.models import Candidate, NON_WHITE_KEY, NON_MALE_KEY
from merepresenta.tests.volunteers import VolunteersTestCaseBase
from backend_candidate.models import CandidacyContact
from elections.models import PersonalData
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from merepresenta.models import VolunteerInCandidate, VolunteerGetsCandidateEmailLog
from django.core import mail


PASSWORD="admin123"


class VolunteerOnlineModelTests(VolunteersTestCaseBase):
    def setUp(self):
        super(VolunteerOnlineModelTests, self).setUp()
        self.volunteer = User.objects.create_user(username="voluntario",
                                                  password=PASSWORD,
                                                  is_staff=True)
        self.candidate = Candidate.objects.get(id=5)

    def test_instanciate(self):
        instance = VolunteerInCandidate.objects.create(volunteer=self.volunteer,
                                                       candidate=self.candidate)
        self.assertTrue(instance.created)


class VolunteerGetsEmailLog(VolunteersTestCaseBase):
    def setUp(self):
        super(VolunteerGetsEmailLog, self).setUp()
        self.volunteer = User.objects.create_user(username="voluntario",
                                                  password=PASSWORD,
                                                  is_staff=True)
        self.candidate = Candidate.objects.get(id=5)

    def test_instanciate(self):
        candidacy_contact = CandidacyContact.objects.create(mail="perrito@gatito.com", candidate=self.candidate)
        log = VolunteerGetsCandidateEmailLog.objects.create(volunteer=self.volunteer,
                                                            contact=candidacy_contact,
                                                            candidate=self.candidate)
        self.assertTrue(log.created)

        self.assertTrue(len(mail.outbox))
        mail_to_candidate = mail.outbox[0]
        self.assertIn(candidacy_contact.mail, mail_to_candidate.to)