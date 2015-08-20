# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections import get_writeit_instance
from django.test.utils import override_settings


@override_settings(WRITEIT_NAME='votainteligente',
                   INSTANCE_URL="/api/v1/instance/1/",
                   WRITEIT_ENDPOINT='http://writeit.ciudadanointeligente.org',
                   WRITEIT_USERNAME='admin',
                   WRITEIT_KEY='a',

                   )
class GloballyCreatedWriteItApi(TestCase):
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
