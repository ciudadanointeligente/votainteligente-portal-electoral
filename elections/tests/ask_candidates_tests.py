# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections import get_writeit_instance
from django.test.utils import override_settings
from elections.models import Election, Candidate, VotaInteligenteMessage
from writeit.models import Message


@override_settings(WRITEIT_NAME='votainteligente',
                   INSTANCE_URL="/api/v1/instance/1/",
                   WRITEIT_ENDPOINT='http://writeit.ciudadanointeligente.org',
                   WRITEIT_USERNAME='admin',
                   WRITEIT_KEY='a',

                   )
class WriteItTestCase(TestCase):
    pass


class GloballyCreatedWriteItApi(WriteItTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_writeit_instance_from_globally_set_variables(self):
        '''There is a function that returns a writeit instance where to push messages'''
        instance = get_writeit_instance()
        self.assertEquals(instance.name, 'votainteligente')
        self.assertEquals(instance.url, "/api/v1/instance/1/")
        self.assertEquals(instance.api_instance.url, 'http://writeit.ciudadanointeligente.org')


class VotaInteligenteMessageTestCase(WriteItTestCase):
    def setUp(self):
        self.instance = get_writeit_instance()
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

    def test_instanciate_a_message(self):
        message = VotaInteligenteMessage.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )

        self.assertTrue(message)
        self.assertIsInstance(message, Message)
