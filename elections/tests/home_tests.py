# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.core.urlresolvers import reverse
from elections.views import HomeView
from elections.forms import ElectionSearchByTagsForm
from elections.models import Election
from django.contrib.auth.forms import AuthenticationForm
from backend_citizen.forms import (UserCreationForm as RegistrationForm,
                                   GroupCreationForm)
from popular_proposal.models import (ProposalTemporaryData,
                                     PopularProposal)
from elections.models import Area
from django.contrib.auth.models import User
import datetime
from django.utils import timezone


class HomeTestCase(TestCase):
    def setUp(self):
        super(HomeTestCase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.feli = User.objects.get(username='feli')
        self.arica = Area.objects.get(id='arica-15101')
        self.alhue = Area.objects.get(id='alhue-13502')
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
        self.assertTemplateUsed(response, 'elections/home.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ElectionSearchByTagsForm)

    def test_home_view(self):
        view = HomeView()
        context = view.get_context_data()

        self.assertIn('form', context)
        self.assertIn('featured_elections', context)
        self.assertIsInstance(context['form'], ElectionSearchByTagsForm)
        self.assertIn('register_new_form', context)
        self.assertIn('login_form', context)
        self.assertIn('group_login_form', context)
        self.assertIsInstance(context['register_new_form'], RegistrationForm)
        self.assertIsInstance(context['login_form'], AuthenticationForm)
        self.assertIsInstance(context['group_login_form'], GroupCreationForm)

    def test_counter_of_proposals(self):
        a_day_ago = timezone.now() - datetime.timedelta(days=1)
        ProposalTemporaryData.objects.create(proposer=self.fiera,
                                             area=self.arica,
                                             created=a_day_ago,
                                             data=self.data)
        ProposalTemporaryData.objects.create(proposer=self.fiera,
                                             area=self.arica,
                                             created=a_day_ago,
                                             data=self.data)
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       created=a_day_ago,
                                       title=u'This is a title',
                                       clasification=u'education'
                                       )
        eight_days_ago = timezone.now() - datetime.timedelta(days=8)
        p1 = PopularProposal.objects.create(proposer=self.fiera,
                                            area=self.arica,
                                            data=self.data,
                                            title=u'This is a title',
                                            clasification=u'education',
                                            created=eight_days_ago
                                            )
        p1.created = eight_days_ago
        p1.save()
        p2 = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                  area=self.arica,
                                                  data=self.data,
                                                  created=eight_days_ago)
        p2.created = eight_days_ago
        p2.save()
        view = HomeView()
        context = view.get_context_data()
        self.assertEquals(context['total_proposals'], 2)
