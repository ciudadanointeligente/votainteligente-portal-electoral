# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.core.urlresolvers import reverse
from popular_proposal.models import PopularProposal
from popular_proposal.forms import ProposalFilterForm


class ProposalViewTestCase(TestCase):
    def setUp(self):
        super(ProposalViewTestCase, self).setUp()

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

class ProposalHomeTestCase(TestCase):
    def setUp(self):
        super(ProposalHomeTestCase, self).setUp()
        self.url = reverse('popular_proposals:home')
        self.popular_proposal1 = PopularProposal.objects.create(proposer=self.fiera,
                                                                area=self.arica,
                                                                data=self.data,
                                                                clasification=u'education',
                                                                title=u'This is a title'
                                                                )
        data2 = self.data
        self.popular_proposal2 = PopularProposal.objects.create(proposer=self.fiera,
                                                                area=self.arica,
                                                                data=data2,
                                                                clasification=u'dogs',
                                                                title=u'This is a title'
                                                                )
        self.popular_proposal3 = PopularProposal.objects.create(proposer=self.fiera,
                                                                area=self.alhue,
                                                                data=data2,
                                                                clasification=u'dogs',
                                                                title=u'This is a title'
                                                                )

    def test_there_is_a_page(self):
        
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('popular_proposals/home.html')

    def test_brings_a_list_of_proposals(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], ProposalFilterForm)

        self.assertIn(self.popular_proposal1, response.context['popular_proposals'])

        self.assertIn(self.popular_proposal2, response.context['popular_proposals'])

        response = self.client.get(self.url, {'clasification': 'dogs', 'area': ''})
        self.assertNotIn(self.popular_proposal1, response.context['popular_proposals'])

        self.assertIn(self.popular_proposal2, response.context['popular_proposals'])


        response = self.client.get(self.url, {'clasification': 'dogs', 'area': self.alhue.id})
        self.assertIn(self.popular_proposal3, response.context['popular_proposals'])
        self.assertNotIn(self.popular_proposal2, response.context['popular_proposals'])
        self.assertNotIn(self.popular_proposal1, response.context['popular_proposals'])

    def test_filtering_form(self):
        data = {'clasification': '', 'area': ''}
        form = ProposalFilterForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data)