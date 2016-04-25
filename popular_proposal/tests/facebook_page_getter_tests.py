# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popular_proposal.tests import ProposingCycleTestCaseBase
from popular_proposal.forms import (ProposalForm,
                                    CommentsForm,
                                    RejectionForm,
                                    ProposalTemporaryDataUpdateForm)
from votainteligente.facebook_page_getter import facebook_getter
import vcr


class FacebookPageGetterTestCase(TestCase):
    def setUp(self):
        super(FacebookPageGetterTestCase, self).setUp()

    @vcr.use_cassette('fixtures/vcr_cassettes/circoroto.yaml')
    def test_get_things_from_facebook(self):
        result = facebook_getter('https://www.facebook.com/circoroto/?fref=ts')
        self.assertEquals(result['about'], u'Agrupación de circo del barrio Yungay')
        self.assertTrue(result['picture_url'])
        self.assertTrue(result['events'])
