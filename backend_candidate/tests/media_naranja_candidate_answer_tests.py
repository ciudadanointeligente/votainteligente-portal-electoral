# coding=utf-8
from candidator.models import TakenPosition, Position
from backend_candidate.forms import (get_field_from_topic,
                                     get_form_class_from_topic,
                                     get_fields_dict_from_topic,
                                     get_form_for_election)
from django import forms
from backend_candidate.tests import SoulMateCandidateAnswerTestsBase


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

    def test_get_dict_with_questions_from_topic(self):
        dict_ = get_fields_dict_from_topic(self.topic)

        self.assertFieldsForTopic(dict_, self.topic)

    def test_get_dict_with_questions_from_topic_initial(self):
        answer = self.topic.positions.get(id=1)
        taken_position = TakenPosition.objects.create(topic=self.topic,
                                                      position=answer,
                                                      person=self.candidate,
                                                      description=u'hello'
                                                      )
        dict_ = get_fields_dict_from_topic(self.topic,
                                           taken_position=taken_position)
        topic_field = dict_['answer_for_' + str(self.topic.id)]
        comments_field = dict_['description_for_' + str(self.topic.id)]
        self.assertEquals(topic_field.initial, answer.id)
        self.assertEquals(comments_field.initial, taken_position.description)

    def test_get_form_for_election(self):
        form_class = get_form_for_election(self.tarapaca)
        form = form_class(candidate=self.candidate)
        for category in self.tarapaca.categories.all():
            for topic in category.topics.all():
                self.assertFieldsForTopic(form.fields, topic)

    def test_form_initial(self):
        answer = self.topic.positions.get(id=1)
        TakenPosition.objects.create(topic=self.topic,
                                     person=self.candidate,
                                     position=answer)
        form_class = get_form_for_election(self.tarapaca)
        form = form_class(candidate=self.candidate)
        field = form.fields['answer_for_' + str(self.topic.id)]
        self.assertEquals(field.initial, answer.id)

    def test_form_saving(self):
        form_class = get_form_for_election(self.tarapaca)
        data = self.get_form_data_for_area(self.tarapaca)
        form = form_class(candidate=self.candidate, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        counter = 0
        for category in self.tarapaca.categories.all():
            for topic in category.topics.all():
                counter += 1
                t_pos = TakenPosition.objects.get(person=self.candidate,
                                                  topic=topic)
                self.assertTrue(t_pos)
                p = Position.objects.get(id=int(data[('answer_for_'
                                                      + str(topic.id))]))
                self.assertEquals(t_pos.position, p)
        self.assertTrue(counter)

    def test_form_updating(self):
        answer = self.topic.positions.get(id=1)
        TakenPosition.objects.create(topic=self.topic,
                                     person=self.candidate,
                                     position=answer)
        form_class = get_form_for_election(self.tarapaca)
        data = self.get_form_data_for_area(self.tarapaca)
        form = form_class(candidate=self.candidate, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        taken_position = TakenPosition.objects.get(topic=self.topic,
                                                   person=self.candidate)
        self.assertTrue(taken_position)