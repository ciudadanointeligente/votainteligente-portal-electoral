# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.models import Candidate, VolunteerGetsCandidateEmailLog
from merepresenta.tests.volunteers import VolunteersTestCaseBase
from merepresenta.voluntarios.forms import AddCandidacyContactForm
from django.contrib.auth.models import User


PASSWORD="admin123"


class CandidateAddCandidacyContactFormTestCase(VolunteersTestCaseBase):
    def setUp(self):
        super(CandidateAddCandidacyContactFormTestCase, self).setUp()
        self.volunteer = User.objects.create_user(username="voluntario",
                                                  password=PASSWORD,
                                                  is_staff=True)

    def test_validate_form(self):
        c = Candidate.objects.get(id=4)
        data = {
            'mail': 'perrito@gatito.com'
        }
        f = AddCandidacyContactForm(candidate=c,
                                    volunteer=self.volunteer,
                                    data=data)
        self.assertTrue(f.is_valid())
        contact = f.save()
        self.assertEquals(contact.mail, data['mail'])

    def test_there_is_created_a_log(self):
        c = Candidate.objects.get(id=4)
        data = {
            'mail': 'perrito@gatito.com'
        }
        f = AddCandidacyContactForm(candidate=c,
                                    volunteer=self.volunteer,
                                    data=data)
        contact = f.save()
        log = VolunteerGetsCandidateEmailLog.objects.get(contact=contact)
        self.assertTrue(log)
        self.assertEquals(log.volunteer, self.volunteer)
        self.assertEquals(log.candidate, c)