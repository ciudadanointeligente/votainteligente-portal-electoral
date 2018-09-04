# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.voluntarios.forms import UpdateAreaForm, VoluntarioCandidateHuntForm
from elections.models import Area
from django.contrib.auth.models import User
from merepresenta.voluntarios.models import VolunteerProfile
from merepresenta.models import Candidate, NON_WHITE_KEY, NON_MALE_KEY, VolunteerGetsCandidateEmailLog
from django.conf import settings
from django.core import mail
from merepresenta.tests.volunteers import VolunteersTestCaseBase


class UpdateAreaForVolunteerForm(TestCase):
    def setUp(self):
        super(UpdateAreaForVolunteerForm, self).setUp()
        self.area = Area.objects.create(name='area')
        self.volunteer = User.objects.create_user(username='volunteer', is_staff=True)
        self.profile = VolunteerProfile.objects.create(user=self.volunteer)


    def test_instanciate_and_save(self):
        data = {
            'area': self.area.id
        }
        form = UpdateAreaForm(data=data, instance=self.profile)
        self.assertTrue(form.is_valid())
        profile = form.save()

        self.assertEquals(profile.area, self.area)


class CandidateSearchForm(VolunteersTestCaseBase):
    def setUp(self):
        super(CandidateSearchForm, self).setUp()
        self.area = Area.objects.create(name='area')
        self.volunteer = User.objects.create_user(username='volunteer', is_staff=True)
        self.profile = VolunteerProfile.objects.create(user=self.volunteer)
        c = Candidate.objects.get(id=5)
        a = c.election.area
        a.classification = settings.FILTERABLE_AREAS_TYPE[0]
        a.save()
        c.race = NON_WHITE_KEY["possible_values"][0]
        c.save()

    def test_instanciate_form(self):
        data = {'facebook': True,
                'tse_email': True,
                'other_email': 'perrito@gatito.com'}
        c = Candidate.objects.get(id=5)
        c.original_email = 'candidaot@tse.com'
        c.save()
        form = VoluntarioCandidateHuntForm(data=data, candidate=c, volunteer=self.volunteer)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.candidate, c)
        self.assertEquals(form.volunteer, self.volunteer)

    def test_send_mail_to_tse_contact(self):
        data = {'facebook': False,
                'tse_email': True,
                'other_email': None}
        c = Candidate.objects.get(id=5)
        c.original_email = 'candidaot@tse.com'
        c.save()
        form = VoluntarioCandidateHuntForm(data=data, candidate=c, volunteer=self.volunteer)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(len(mail.outbox))
        mail_to_candidate = mail.outbox[0]
        self.assertIn(c.original_email, mail_to_candidate.to)

    def test_send_mail_to_found_contact(self):
        data = {'facebook': False,
                'tse_email': False,
                'other_email': 'new_email@google.com'}
        c = Candidate.objects.get(id=5)
        c.original_email = 'candidaot@tse.com'
        c.save()
        form = VoluntarioCandidateHuntForm(data=data, candidate=c, volunteer=self.volunteer)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(len(mail.outbox))
        mail_to_candidate = mail.outbox[0]
        self.assertIn('new_email@google.com', mail_to_candidate.to)

    def test_found_facebook(self):
        data = {'facebook': True,
                'tse_email': False,
                'other_email': None}
        c = Candidate.objects.get(id=5)
        c.original_email = 'candidaot@tse.com'
        c.save()
        form = VoluntarioCandidateHuntForm(data=data, candidate=c, volunteer=self.volunteer)
        self.assertTrue(form.is_valid())
        form.save()
        c.refresh_from_db()
        self.assertTrue(c.contacts.all())

    def test_if_nothing_found_then_ghost(self):
        data = {'facebook': False,
                'tse_email': False,
                'other_email': None}
        c = Candidate.objects.get(id=5)
        form = VoluntarioCandidateHuntForm(data=data, candidate=c, volunteer=self.volunteer)
        self.assertTrue(form.is_valid())
        form.save()
        c.refresh_from_db()
        self.assertTrue(c.is_ghost)
        log = VolunteerGetsCandidateEmailLog.objects.get(volunteer=self.volunteer, candidate=c)
        self.assertTrue(log)