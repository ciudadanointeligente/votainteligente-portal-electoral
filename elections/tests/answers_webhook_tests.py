# coding=utf-8
from elections.models import Election, VotaInteligenteMessage, VotaInteligenteAnswer
from tastypie.test import ResourceTestCase
from django.test.utils import override_settings


class ElectionSearchFormTestCase(ResourceTestCase):
    fixtures = ['example_data_mini.yaml']

    def setUp(self):
        super(ElectionSearchFormTestCase, self).setUp()
        self.election = Election.objects.all()[0]
        self.candidate1 = self.election.popit_api_instance.person_set.all()[0]
        self.candidate2 = self.election.popit_api_instance.person_set.all()[1]
        self.message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message.people.add(self.candidate1)

        self.message.push_to_the_api()


    @override_settings(NEW_ANSWER_ENDPOINT = 'new_answer_comming_expected_to_be_a_hash')
    def test_when_i_post_to_a_point_it_creates_an_answer(self):

        response = self.api_client.post('/api/v1/%s/' % ('new_answer_comming_expected_to_be_a_hash') , 
            format='json', 
            data = {
                'content': 'Example Answer', \
                'person': self.candidate1.name, \
                'person_id': self.candidate1.popit_url, \
                'message_id': self.message.url
            }
        )
        self.assertHttpCreated(response)
        self.assertEquals(self.message.answers.count(), 1)
        answer = self.message.answers.all()[0]
        self.assertEquals(answer.content, 'Example Answer')
        self.assertEquals(answer.person, self.candidate1)