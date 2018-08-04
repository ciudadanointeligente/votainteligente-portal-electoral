# coding=utf-8
from candidator.models import TakenPosition, Position
from django.test import TestCase, override_settings
from merepresenta.models import Candidate, NON_WHITE_KEY, NON_MALE_KEY
from merepresenta.tests.volunteers import VolunteersTestCaseBase
from backend_candidate.models import CandidacyContact, Candidacy
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
import mock
from django.views.generic.edit import FormView
from django.core import mail
from merepresenta.models import (VolunteerInCandidate,
                                 VolunteerGetsCandidateEmailLog,
                                 Candidate,
                                 QuestionCategory)
from merepresenta.voluntarios.models import VolunteerProfile
from elections.models import PersonalData, Area, Election, Topic
from django.conf import settings
import datetime
from merepresenta.candidatos.forms import (CPFAndDdnForm,
                                           CPFAndDdnForm2,
                                           get_form_class_from_category,
                                           get_form_classes_for_questions_for)
from django import forms


PASSWORD = 'candidato123'


class assertFieldsForTopicMixin(object):
    def assertFieldsForTopic(self, dict_, original_topic):

        topic = dict_['answer_for_' + str(original_topic.id)]
        self.assertIsInstance(topic, forms.ChoiceField)
        self.assertIsInstance(topic.widget, forms.RadioSelect)

        comments = dict_['description_for_' + str(original_topic.id)]
        self.assertIsInstance(comments, forms.CharField)
        self.assertIsInstance(comments.widget, forms.TextInput)


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class CompletePautasTestCase(VolunteersTestCaseBase, assertFieldsForTopicMixin):
    def setUp(self):
        super(CompletePautasTestCase, self).setUp()
        QuestionCategory.objects.all().delete()
        self.d = datetime.datetime(2009, 10, 5, 18, 00)
        self.area = Area.objects.create(name="area")
        self.election = Election.objects.create(name='ele', area=self.area)
        self.candidate = Candidate.objects.create(name='THE candidate', cpf='1234', data_de_nascimento=self.d)

    def test_get_form_from_category(self): 
        cat = QuestionCategory.objects.create(name="Pautas LGBT")
        topic = Topic.objects.create(label=u"Adoção de crianças por famílias LGBTs", category=cat)
        yes = Position.objects.create(topic=topic, label=u"Sou a FAVOR da adoção de crianças por famílias LGBTs")
        no = Position.objects.create(topic=topic, label=u"Sou CONTRA a adoção de crianças por famílias LGBTs")

        topic2 = Topic.objects.create(label=u"é A favor?", category=cat)
        yes2 = Position.objects.create(topic=topic, label=u"Sou a FAVOR")
        no2 = Position.objects.create(topic=topic, label=u"Sou CONTRA")

        form = get_form_class_from_category(category=cat, candidate=self.candidate)()
        self.assertTrue(form)
        for topic in cat.topics.all():
            self.assertFieldsForTopic(form.fields, topic)

    def test_get_list_of_forms(self):
        cat = QuestionCategory.objects.create(name="Pautas LGBT")
        topic = Topic.objects.create(label=u"Adoção de crianças por famílias LGBTs", category=cat)
        yes = Position.objects.create(topic=topic, label=u"Sou a FAVOR da adoção de crianças por famílias LGBTs")
        no = Position.objects.create(topic=topic, label=u"Sou CONTRA a adoção de crianças por famílias LGBTs")

        topic2 = Topic.objects.create(label=u"é A favor?", category=cat)
        yes2 = Position.objects.create(topic=topic, label=u"Sou a FAVOR")
        no2 = Position.objects.create(topic=topic, label=u"Sou CONTRA")

        cat2 = QuestionCategory.objects.create(name="Pautas LGBT")
        topic3 = Topic.objects.create(label=u"Adoção de crianças por famílias LGBTs", category=cat)
        yes3 = Position.objects.create(topic=topic, label=u"Sou a FAVOR da adoção de crianças por famílias LGBTs")
        no3 = Position.objects.create(topic=topic, label=u"Sou CONTRA a adoção de crianças por famílias LGBTs")

        topic4 = Topic.objects.create(label=u"é A favor?", category=cat)
        yes4 = Position.objects.create(topic=topic, label=u"Sou a FAVOR")
        no4 = Position.objects.create(topic=topic, label=u"Sou CONTRA")

        form_classes = get_form_classes_for_questions_for(self.candidate)
        for form_class in form_classes:
            form = form_class()
            self.assertIn(form.category, [cat, cat2])