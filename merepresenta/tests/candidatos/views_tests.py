# coding=utf-8
from candidator.models import Position
from backend_candidate.tests import SoulMateCandidateAnswerTestsBase
from django.test import override_settings, modify_settings
from merepresenta.models import Candidate, QuestionCategory
from merepresenta.forms import PersonalDataForm
from backend_candidate.forms import get_candidate_profile_form_class
from backend_candidate.models import Candidacy
from django.contrib.auth.models import User
from elections.models import PersonalData, Election, Area, Topic
from django.template import Template, Context
from django.core.urlresolvers import reverse
from popolo.models import ContactDetail
import datetime


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class CandidateProfileView(SoulMateCandidateAnswerTestsBase):
    def setUp(self):
        super(CandidateProfileView, self).setUp()
        self.d = datetime.datetime(2009, 10, 5, 18, 00)
        self.area = Area.objects.create(name="area")
        self.election = Election.objects.create(name='ele', area=self.area)
        self.candidate = Candidate.objects.create(name='THE candidate', cpf='1234', data_de_nascimento=self.d)

    def test_get_the_profile(self):
        url = reverse('candidate_profile', kwargs={'slug': self.candidate.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['candidate'], self.candidate)
        self.assertTemplateUsed(response, 'merepresenta/candidate_detail.html')

    def test_getting_the_detail_view_brings_all_the_question_categories(self):
        cat = QuestionCategory.objects.create(name="Pautas LGBT")
        topic = Topic.objects.create(label=u"Adoção de crianças por famílias LGBTs", category=cat)
        yes = Position.objects.create(topic=topic, label=u"Sou a FAVOR da adoção de crianças por famílias LGBTs")
        no = Position.objects.create(topic=topic, label=u"Sou CONTRA a adoção de crianças por famílias LGBTs")

        url = reverse('candidate_profile', kwargs={'slug': self.candidate.slug})
        response = self.client.get(url)
        self.assertIn(cat, response.context['categories'])


