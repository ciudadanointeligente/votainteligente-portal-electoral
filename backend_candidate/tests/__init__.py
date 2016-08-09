# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, Candidate
from candidator.models import Topic
from django import forms
import theme

class SoulMateCandidateAnswerTestsBase(TestCase):
    def setUp(self):
        super(SoulMateCandidateAnswerTestsBase, self).setUp()
        self.tarapaca = Election.objects.get(id=1)
        self.topic = Topic.objects.get(id=1)
        self.candidate = Candidate.objects.get(id=1)

    def assertFieldsForTopic(self, dict_, topic):

        topic = dict_['answer_for_' + str(self.topic.id)]
        self.assertIsInstance(topic, forms.ChoiceField)
        self.assertIsInstance(topic.widget, forms.RadioSelect)

        comments = dict_['description_for_' + str(self.topic.id)]
        self.assertIsInstance(comments, forms.CharField)
        self.assertIsInstance(comments.widget, forms.TextInput)

    def get_data_for_topic(self, topic):
        answer_key = 'answer_for_' + str(topic.id)
        position = topic.positions.all().order_by('?')[0]
        description_key = 'description_for_' + str(topic.id)
        dict_ = {answer_key: position.id,
                 description_key: ""}
        return dict_

    def get_form_data_for_area(self, area):
        data = {}
        for category in area.categories.all():
            for topic in category.topics.all():
                data.update(self.get_data_for_topic(topic))
        return data