# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from popular_proposal.models import ProposalTemporaryData, PopularProposal, ProposalLike
from rest_framework.test import APIClient
from rest_framework.reverse import reverse


class PopularProposalRestAPITestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalRestAPITestCase, self).setUp()
        self.client = APIClient()

    def test_get_proposal(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                      )
        url = reverse('popularproposal-list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
