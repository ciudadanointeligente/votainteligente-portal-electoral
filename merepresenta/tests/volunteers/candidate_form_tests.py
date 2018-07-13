# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.models import Candidate
from merepresenta.tests.volunteers import VolunteersTestCaseBase
from merepresenta.voluntarios.forms import AddCandidacyContactForm


class CandidateAddCandidacyContactFormTestCase(VolunteersTestCaseBase):
    def setUp(self):
        super(CandidateAddCandidacyContactFormTestCase, self).setUp()

    def test_validate_form(self):
        c = Candidate.objects.get(id=4)
        data = {
            'mail': 'perrito@gatito.com'
        }
        f = AddCandidacyContactForm(candidate=c, data=data)
        self.assertTrue(f.is_valid())
        f.save()
        contact = c.contacts.first()
        self.assertEquals(contact.mail, data['mail'])
