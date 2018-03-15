# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.test import override_settings
from elections.models import Candidate
from backend_candidate.forms import get_candidate_profile_form_class
from backend_candidate.models import Candidacy
from django.contrib.auth.models import User
from elections.models import PersonalData, Election
from django.template import Template, Context
from django.core.urlresolvers import reverse
from backend_candidate.forms import get_candidate_profile_form_class
from popolo.models import ContactDetail
import datetime
from agenda.models import Activity
from django.utils import timezone


class AgendaViewTestCase(TestCase):
    def setUp(self):
        self.feli = User.objects.get(username='feli')
        self.feli.set_password('alvarez')
        self.feli.save()
        self.candidate = Candidate.objects.get(pk=1)
        self.candidacy = Candidacy.objects.create(user=self.feli,
                                                  candidate=self.candidate)

    def test_get_create_an_activity_from_view(self):
        url = reverse('backend_candidate:add_activity', kwargs={'slug': self.candidate.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        
        not_the_right_candidate = Candidate.objects.create(name='Not the right candidate')
        self.client.login(username=self.feli,
                          password='alvarez')
        not_the_right_url = reverse('backend_candidate:add_activity',
                                    kwargs={'slug': not_the_right_candidate.slug})
        response = self.client.get(not_the_right_url)
        self.assertEquals(response.status_code, 404)
        
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_candidate/add_activity.html')
        self.assertEquals(response.context['object'], self.candidate)
        
    def test_posting_to_create_an_activity(self):
        url = reverse('backend_candidate:add_activity', kwargs={'slug': self.candidate.slug})
        self.client.login(username=self.feli,
                          password='alvarez')
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        ## '%Y-%m-%d %H:%M:%S'
        data = {
            'date': tomorrow.strftime('%Y-%m-%d %H:%M:%S'),
            'url': 'https://perrito.cl/actividad_secreta',
            'description': 'This is a description',
            'location': 'secret location'
        }
        response = self.client.post(url, data=data)
        print self.candidate.slug, url
        url_complete_profile = reverse('backend_candidate:all_my_activities',
                                       kwargs={'slug':self.candidate.slug})
        self.assertRedirects(response, url_complete_profile)
        self.assertTrue(self.candidate.agenda.all())
    
    def test_see_my_agenda(self):
        url = reverse('backend_candidate:all_my_activities', kwargs={'slug': self.candidate.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        
        not_the_right_candidate = Candidate.objects.create(name='Not the right candidate')
        self.client.login(username=self.feli,
                          password='alvarez')
        not_the_right_url = reverse('backend_candidate:all_my_activities',
                                    kwargs={'slug': not_the_right_candidate.slug})
        response = self.client.get(not_the_right_url)
        self.assertEquals(response.status_code, 404)
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        
        activity1 = Activity.objects.create(date=tomorrow,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='This is a description',
                                            content_object=self.candidate,
                                            location='secret location')
        another_candidate = Candidate.objects.get(id=2)
        activity2 = Activity.objects.create(date=tomorrow,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='This is a description',
                                            content_object=another_candidate,
                                            location='secret location')
        
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_candidate/all_my_activities.html')
        self.assertEquals(response.context['object'], self.candidate)
        self.assertIn(activity1, response.context['activities'].all())
        self.assertNotIn(activity2, response.context['activities'].all())