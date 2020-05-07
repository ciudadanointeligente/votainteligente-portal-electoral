# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.core.urlresolvers import reverse
from elections.views import HomeView
from elections.forms import ElectionSearchByTagsForm
from elections.models import Election, Candidate
from elections.models import Area
from django.contrib.auth.models import User
from django.test import override_settings


class HomeTestCase(TestCase):
    def setUp(self):
        super(HomeTestCase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.feli = User.objects.get(username='feli')
        self.arica = Area.objects.get(id=3)
        self.alhue = Area.objects.get(id=2)
        self.data = {
            'clasification': 'educacion',
            'title': u'Fiera a Santiago',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos\
 y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'causes': u'La super distancia',
            'terms_and_conditions': True
        }

    def test_get_home(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ElectionSearchByTagsForm)

    @override_settings(IMPORTANT_CANDIDATE_IN_LANDING=1)
    def test_if_candidate_in_settings_then_bring_it(self):
        view = HomeView()
        context = view.get_context_data()
        expected_candidate = Candidate.objects.get(id=1)
        self.assertEquals(context['important_candidate'], expected_candidate)
