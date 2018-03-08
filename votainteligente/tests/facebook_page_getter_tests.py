# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from votainteligente.facebook_page_getter import facebook_getter
import vcr
import os 
__dir__ = os.path.dirname(os.path.realpath(__file__))


class FacebookPageGetterTestCase(TestCase):
    def setUp(self):
        super(FacebookPageGetterTestCase, self).setUp()

    @vcr.use_cassette(__dir__ + '/fixtures/vcr_cassettes/circoroto.yaml')
    def test_get_things_from_facebook(self):
        result = facebook_getter('https://www.facebook.com/circoroto?fref=ts')
        self.assertEquals(result['about'], u'Agrupación de circo del barrio Yungay')
        self.assertTrue(result['picture_url'])
        self.assertTrue(result['events'])
