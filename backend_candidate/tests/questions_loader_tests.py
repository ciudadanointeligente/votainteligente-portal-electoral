# coding=utf-8
from candidator.models import TakenPosition, Position
from backend_candidate.forms import (get_field_from_topic,
                                     get_form_class_from_topic,
                                     get_fields_dict_from_topic,
                                     get_form_for_election)
from elections.models import Election, QuestionCategory
from django.core.management import call_command
from backend_candidate.tests import SoulMateCandidateAnswerTestsBase


class QuestionsLoaderTestCase(SoulMateCandidateAnswerTestsBase):
    def setUp(self):
        super(QuestionsLoaderTestCase, self).setUp()

    def test_questions_loading(self):
    	QuestionCategory.objects.all().delete()
    	call_command('load_questions', 'backend_candidate/tests/fixtures/questions.yaml')
    	election = Election.objects.get(id=1)
    	self.assertEquals(len(election.categories.all()), 1)
    	category = election.categories.all()[0]
    	self.assertEquals(category.name, u"preguntas Buenas")

    	self.assertEquals(len(category.topics.all()), 2)
    	question1 = category.topics.get(label=u"Esto es una pregunta y quiero una respuesta")
    	self.assertTrue(question1.label, u"Esto es una pregunta y quiero una respuesta")
    	question2 = category.topics.get(label=u"Pregunta 2")

    	a1 = question1.positions.get(label=u"Respuesta 1")
    	a2 = question1.positions.get(label=u"Respuesta 2")
    	a3 = question1.positions.get(label=u"Respuesta 3")

    	a4 = question2.positions.get(label=u"Respuesta 4")
    	a5 = question2.positions.get(label=u"Respuesta 5")
    	a6 = question2.positions.get(label=u"Respuesta 3")
    	self.assertTrue(a1)
    	self.assertTrue(a2)
    	self.assertTrue(a3)
    	self.assertTrue(a4)
    	self.assertTrue(a5)
    	self.assertTrue(a6)
