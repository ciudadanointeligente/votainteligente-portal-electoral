# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.models import Candidate, NON_WHITE_KEY, NON_MALE_KEY
from merepresenta.tests.volunteers import VolunteersTestCaseBase
from backend_candidate.models import CandidacyContact
from elections.models import PersonalData, Election, Area
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from merepresenta.models import VolunteerInCandidate, VolunteerGetsCandidateEmailLog
from django.core import mail
from merepresenta.voluntarios.filters import CandidateFilter


PASSWORD="admin123"
ESTADO_IDENTIFIER = 'TO'

class CandidateFilterTests(VolunteersTestCaseBase):
    def setUp(self):
        super(CandidateFilterTests, self).setUp()
        self.volunteer = User.objects.create_user(username="voluntario",
                                                  password=PASSWORD,
                                                  is_staff=True)
        self.area = Area.objects.get(identifier=ESTADO_IDENTIFIER)
        self.election = Election.objects.create(name="Deputado Estadual")
        self.election.area = self.area
        self.election.save()
        self.candidate = Candidate.objects.get(id=5)
        self.election.candidates.add(self.candidate)
        self.candidate2 = Candidate.objects.get(id=4)

    def test_filter(self):
        data = {'elections__area': '',}
        _filter = CandidateFilter(data=data)
        form = _filter.form
        self.assertTrue(form.is_valid())
        qs = _filter.qs
        self.assertIn(self.candidate, qs)
        self.assertIn(self.candidate2, qs)
        
        data = {'elections__area': self.area.id}
        _filter = CandidateFilter(data=data)
        qs = _filter.qs
        self.assertIn(self.candidate, qs)
        self.assertNotIn(self.candidate2, qs)