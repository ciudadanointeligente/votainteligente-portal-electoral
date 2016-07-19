# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, Candidate
from candidator.models import Topic
from backend_candidate.forms import (get_field_from_topic,
                                     get_form_class_from_topic,
                                     get_fields_dict_from_topic,
                                     get_form_for_area)
from django import forms

class SoulMateCandidateAnswerTestsBase(TestCase):
    def setUp(self):
        super(SoulMateCandidateAnswerTestsBase, self).setUp()
        self.tarapaca = Election.objects.get(id=1)
        self.topic = Topic.objects.get(id=1)
        self.candidate = Candidate.objects.get(id=1)


class SoulMateCandidateAnswerTests(SoulMateCandidateAnswerTestsBase):
    def setUp(self):
        super(SoulMateCandidateAnswerTests, self).setUp()

    def test_get_question_form_from_question(self):
        field = get_field_from_topic(self.topic)
        self.assertIsInstance(field, forms.ChoiceField)
        self.assertIsInstance(field.widget, forms.RadioSelect)
        self.assertEquals(field.label, self.topic.label)

        self.assertTrue(field.choices)
        self.assertTrue(self.topic.positions.all())
        for p in self.topic.positions.all():
            self.assertIn((p.id, p.label), field.choices)

    def test_get_form_from_topic(self):
        form_class = get_form_class_from_topic(self.topic)
        form = form_class(candidate=self.candidate)
        self.assertIsInstance(form, forms.Form)
        self.assertEquals(len(form.fields), 3)
        #  Fields
        hidden = form.fields['topic_id']
        self.assertIsInstance(hidden, forms.IntegerField)
        self.assertIsInstance(hidden.widget, forms.HiddenInput)
        self.assertEquals(hidden.initial, self.topic.id)

        topic = form.fields['answer']
        self.assertIsInstance(topic, forms.ChoiceField)
        self.assertIsInstance(topic.widget, forms.RadioSelect)

        comments = form.fields['description']
        self.assertIsInstance(comments, forms.CharField)
        self.assertIsInstance(comments.widget, forms.TextInput)

    def test_form_validation_and_saving(self):
        form_class = get_form_class_from_topic(self.topic)
        answer = self.topic.positions.get(id=1)
        data = {'topic_id': self.topic.id,
                'answer': answer.id,
                'description': 'description'
                }
        form = form_class(candidate=self.candidate, data=data)
        self.assertTrue(form.is_valid())
        taken_position = form.save()
        self.assertEquals(taken_position.topic, self.topic)
        self.assertEquals(taken_position.position, answer)
        self.assertEquals(taken_position.person, self.candidate)
        self.assertEquals(taken_position.description, 'description')

class FullMediaNaranjaQuestionaryForCandidates(SoulMateCandidateAnswerTestsBase):
    def setUp(self):
        super(FullMediaNaranjaQuestionaryForCandidates, self).setUp()

    def assertFieldsForTopic(self, dict_, topic):
        hidden = dict_['topic_' + str(self.topic.id)]
        self.assertIsInstance(hidden, forms.IntegerField)
        self.assertIsInstance(hidden.widget, forms.HiddenInput)
        self.assertEquals(hidden.initial, self.topic.id)

        topic = dict_['answer_for_' + str(self.topic.id)]
        self.assertIsInstance(topic, forms.ChoiceField)
        self.assertIsInstance(topic.widget, forms.RadioSelect)

        comments = dict_['description_for_' + str(self.topic.id)]
        self.assertIsInstance(comments, forms.CharField)
        self.assertIsInstance(comments.widget, forms.TextInput)


    def test_get_dict_with_questions_from_topic(self):
        dict_ = get_fields_dict_from_topic(self.topic)

        self.assertFieldsForTopic(dict_, self.topic)

    def test_get_form_for_area(self):
        form_class = get_form_for_area(self.tarapaca)
        form = form_class()
        for category in self.tarapaca.categories.all():
            for topic in category.topics.all():
                self.assertFieldsForTopic(form.fields, topic)