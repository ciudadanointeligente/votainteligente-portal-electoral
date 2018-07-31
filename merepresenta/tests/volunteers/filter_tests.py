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


@override_settings(FILTERABLE_AREAS_TYPE=['state',])
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



@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class VolunteersIndexViewWithFilterTests(VolunteersTestCaseBase):
    def setUp(self):
        super(VolunteersIndexViewWithFilterTests, self).setUp()

    def create_ordered_candidates(self):
        Candidate.objects.filter(id__in=[4, 5]).update(gender=NON_MALE_KEY)
        cs = Candidate.objects.filter(id__in=[4,5])
        self.assertEquals(cs[0].is_women, 1)
        self.assertEquals(cs[1].is_women, 1)
        c = Candidate.objects.get(id=5)
        c.race = NON_WHITE_KEY["possible_values"][0]
        c.save()

    def test_get_index(self):
        url = reverse('volunteer_index')

        u = User.objects.create_user(username="new_user", password="abc", is_staff=True)
        self.client.login(username=u.username, password="abc")
        response = self.client.get(url)

        self.create_ordered_candidates()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['filter'])