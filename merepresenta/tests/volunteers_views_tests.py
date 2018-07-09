# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.models import Candidate, NON_WHITE_KEY, NON_MALE_KEY
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import PersonalData
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class VolunteersViewsTests(TestCase):
    def setUp(self):
        super(VolunteersViewsTests, self).setUp()

    def create_ordered_candidates(self):
        Candidate.objects.filter(id__in=[4, 5]).update(gender=NON_MALE_KEY)
        cs = Candidate.objects.filter(id__in=[4,5])
        self.assertEquals(cs[0].is_women, 1)
        self.assertEquals(cs[1].is_women, 1)
        c = Candidate.objects.get(id=5)
        personal_data = PersonalData.objects.create(label=u'Cor e raça',
                                                    value=NON_WHITE_KEY["possible_values"][0],
                                                    candidate=c)

    def test_get_index(self):
        url = reverse('volunteer_index')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        u = User.objects.create_user(username="new_user", password="abc")
        self.client.login(username=u.username, password="abc")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

        u.is_staff = True
        u.save()
        self.create_ordered_candidates()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        candidates = response.context['candidates']
        self.assertEquals(int(candidates[0].id), 5)

