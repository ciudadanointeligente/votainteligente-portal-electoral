# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from hitcount.models import HitCount
from popular_proposal.models import PopularProposal


class PopularProposalHitCountTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalHitCountTestCase, self).setUp()

    def test_instantiate_get_hit_count(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        hit_count = HitCount.objects.get_for_object(popular_proposal)
        self.assertTrue(hit_count)
        self.assertEquals(hit_count.hits, 0)
        self.client.get(popular_proposal.get_absolute_url())
        hit_count = HitCount.objects.get_for_object(popular_proposal)
        self.assertEquals(hit_count.hits, 1)
