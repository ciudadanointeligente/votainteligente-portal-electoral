# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.core.urlresolvers import reverse
from popular_proposal.models import PopularProposal


class ProposalViewTestCase(TestCase):
    def setUp(self):
        super(ProposalViewTestCase, self).setUp()

    def test_there_is_a_page(self):
        url = reverse('popular_proposals:home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('popular_proposals/home.html')
    
    # def test_there_is_a_page_for_popular_proposal(self):
    #     popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
    #                                                       area=self.arica,
    #                                                       data=self.data,
    #                                                       title=u'This is a title'
    #                                                       )
    #     # no need to be logged in
    #     url = reverse('popular_proposals:detail', kwargs={''})