# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.core.urlresolvers import reverse
from popular_proposal.models import PopularProposal, Organization


class OrganizationDetailViewTests(TestCase):
    def setUp(self):
        super(OrganizationDetailViewTests, self).setUp()
        self.organization = Organization.objects.create(name=u'La cossa nostra')

    def test_there_is_a_url(self):
        url = reverse('popular_proposals:organization', kwargs={'slug': self.organization.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'popular_proposal/organization.html')
        self.assertEquals(response.context['organization'], self.organization)

class ProposalViewTestCase(TestCase):
    def setUp(self):
        super(ProposalViewTestCase, self).setUp()

    def test_there_is_a_page(self):
        url = reverse('popular_proposals:home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('popular_proposals/home.html')

    def test_there_is_a_page_for_popular_proposal(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title'
                                                          )
        # no need to be logged in
        url = reverse('popular_proposals:detail', kwargs={'slug': popular_proposal.slug})
        self.assertEquals(popular_proposal.get_absolute_url(), url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.context['popular_proposal'], popular_proposal)
        self.assertTemplateUsed(response, 'popular_proposal/detail.html')

    def test_thanks_page(self):
        url = reverse('popular_proposals:thanks', kwargs={'pk': self.arica.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['area'], self.arica)

