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
                                 CandidateQuestionCategory,
                                 QuestionCategory)
from merepresenta.voluntarios.models import VolunteerProfile
from elections.models import PersonalData, Area, Election, Topic
from django.conf import settings
import datetime
from merepresenta.candidatos.forms import (CPFAndDdnForm,
                                           CPFAndDdnForm2,
                                           get_form_class_from_category,
                                           get_form_classes_for_questions_for,
                                           CategoryCandidateForm)
from django import forms
from django.forms.models import ModelMultipleChoiceField

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
        for form_class in form_classes[:2]:
            form = form_class()
            self.assertIn(form.category, [cat, cat2])

    def test_get_the_view_has_wizard(self):
        url = reverse('complete_pautas')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('index'))
        voluntario = User.objects.create_user(username='voluntario', password=PASSWORD, is_staff=True)
        logged_in = self.client.login(username=voluntario.username, password=PASSWORD)
        self.assertTrue(logged_in)
        response = self.client.get(url)
        self.assertRedirects(response, reverse('index'))
        candidato_user = User.objects.create_user(username='candidato', password=PASSWORD)
        Candidacy.objects.create(user=candidato_user, candidate=self.candidate)
        self.client.login(username=candidato_user.username, password=PASSWORD)

        cat = QuestionCategory.objects.create(name="Pautas LGBT")
        topic = Topic.objects.create(label=u"Adoção de crianças por famílias LGBTs", category=cat)
        yes = Position.objects.create(topic=topic, label=u"Sou a FAVOR da adoção de crianças por famílias LGBTs")
        no = Position.objects.create(topic=topic, label=u"Sou CONTRA a adoção de crianças por famílias LGBTs")

        response = self.client.get(url)
        self.assertIn('wizard', response.context)

    def test_last_form(self):
        cat1 = QuestionCategory.objects.create(name="Pautas LGBT")
        cat2 = QuestionCategory.objects.create(name="Pautas Raciales")
        data = {
            'categories': [cat1.id, cat2.id]
        }
        form = CategoryCandidateForm(candidate=self.candidate, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        candidate_categories = CandidateQuestionCategory.objects.filter(candidate=self.candidate)
        self.assertTrue( candidate_categories.filter(category=cat1))
        self.assertTrue( candidate_categories.filter(category=cat2))

    def test_posting_to_the_view(self):
        url = reverse('complete_pautas')
        candidato_user = User.objects.create_user(username='candidato', password=PASSWORD)
        Candidacy.objects.create(user=candidato_user, candidate=self.candidate)
        self.client.login(username=candidato_user.username, password=PASSWORD)

        cat = QuestionCategory.objects.create(name="Pautas LGBT")
        topic = Topic.objects.create(label=u"Adoção de crianças por famílias LGBTs", category=cat)
        yes = Position.objects.create(topic=topic, label=u"Sou a FAVOR da adoção de crianças por famílias LGBTs")
        no = Position.objects.create(topic=topic, label=u"Sou CONTRA a adoção de crianças por famílias LGBTs")

        cat2 = QuestionCategory.objects.create(name="2222")
        topic2 = Topic.objects.create(label=u"2222topic222", category=cat2)
        yes2 = Position.objects.create(topic=topic2, label=u"yes22")
        no2 = Position.objects.create(topic=topic2, label=u"nao22")

        response = self.client.get(url)
        steps = response.context['wizard']['steps']
        
        for i in range(steps.count):
            form = response.context['wizard']['form']
            fields = form.fields
            keys = fields.keys()
            data = {}
            for key in keys:
                field_name = "%d-%s" % (i, key)
                if hasattr(fields[key], 'choices') and not isinstance(fields[key], ModelMultipleChoiceField):
                    choice = fields[key].choices[0]
                    
                    data[field_name] = choice[0]
                elif isinstance(fields[key], ModelMultipleChoiceField):
                    ids = [cat.id, cat2.id]
                    data[field_name] = ids

            data.update({'on_demand_complete_pautas-current_step': unicode(i)})
            response = self.client.post(url, data=data)
        
        taken_positions = TakenPosition.objects.filter(person=self.candidate)
        self.assertTrue(taken_positions.filter(topic=topic))
        tp1 = taken_positions.get(topic=topic)
        self.assertIsNotNone(tp1.position)
        self.assertTrue(taken_positions.filter(topic=topic2))
        tp2 = taken_positions.get(topic=topic2)
        self.assertIsNotNone(tp2.position)