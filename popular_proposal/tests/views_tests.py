# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.core.urlresolvers import reverse
from django.forms import Form
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     ProposalTemporaryData)
from popular_proposal.filters import (ProposalFilterBase)
from backend_candidate.models import Candidacy
from popular_proposal.forms import (AuthorityCommitmentForm,
                                    AuthorityNotCommitingForm,
                                    )
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from constance.test import override_config
from django.test import override_settings


class PopularProposalTestCaseBase(TestCase):
    def setUp(self):
        super(PopularProposalTestCaseBase, self).setUp()
        self.popular_proposal1 = PopularProposal.objects.create(proposer=self.fiera,
                                                                data=self.data,
                                                                clasification=TOPIC_CHOICES[1][0],
                                                                title=u'This is a title'
                                                                )
        data2 = self.data
        self.popular_proposal2 = PopularProposal.objects.create(proposer=self.fiera,
                                                                data=data2,
                                                                clasification=TOPIC_CHOICES[2][0],
                                                                title=u'This is a title'
                                                                )
        self.popular_proposal3 = PopularProposal.objects.create(proposer=self.fiera,
                                                                data=data2,
                                                                clasification=TOPIC_CHOICES[2][0],
                                                                title=u'This is a title'
                                                                )


class ProposalViewTestCase(TestCase):
    def setUp(self):
        super(ProposalViewTestCase, self).setUp()

    def test_there_is_a_page_for_popular_proposal(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
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
    
    def test_detail_redirect_view(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          data=self.data,
                                                          title=u'This is a title'
                                                          )
        # no need to be logged in
        url = reverse('popular_proposals:short_detail', kwargs={'pk': popular_proposal.pk})
        response = self.client.get(url)
        self.assertRedirects(response, popular_proposal.get_absolute_url())
        self.assertEquals(popular_proposal.get_short_url(), url)

    def test_proposal_og_image(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          data=self.data,
                                                          title=u'This is a title'
                                                          )
        url = reverse('popular_proposals:og_image',
                      kwargs={'slug': popular_proposal.slug})
        response = self.client.get(url)
        self.assertIn("image/", response['Content-Type'])

    def test_embedded_detail_popular_proposal(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          data=self.data,
                                                          title=u'This is a title'
                                                          )
        # no need to be logged in
        url = reverse('popular_proposals:embedded_detail',
                      kwargs={'slug': popular_proposal.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.context['layout'], 'embedded_base.html')
        self.assertEqual(response.context['popular_proposal'],
                         popular_proposal)
        self.assertTemplateUsed(response,
                                'popular_proposal/detail.html')
        self.assertTemplateUsed(response,
                                'embedded_base.html')
        self.assertTrue(response.context['is_embedded'])


class ProposalHomeTestCase(PopularProposalTestCaseBase):
    def setUp(self):
        super(ProposalHomeTestCase, self).setUp()
        self.url = reverse('popular_proposals:home')

    def test_there_is_a_page(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'popular_proposal/home.html')

    def test_brings_a_list_of_proposals(self):
        response = self.client.get(self.url, {})
        self.assertIsInstance(response.context['form'], Form)

        self.assertIn(self.popular_proposal1, response.context['popular_proposals'])

        self.assertIn(self.popular_proposal2, response.context['popular_proposals'])

        response = self.client.get(self.url, {'clasification': TOPIC_CHOICES[2][0]})
        form = response.context['form']
        self.assertEquals(form.fields['clasification'].initial, TOPIC_CHOICES[2][0])
        self.assertNotIn(self.popular_proposal1, response.context['popular_proposals'])

        self.assertIn(self.popular_proposal2, response.context['popular_proposals'])

        response = self.client.get(self.url, {'clasification': TOPIC_CHOICES[2][0]})
        form = response.context['form']
        self.assertEquals(form.fields['clasification'].initial, TOPIC_CHOICES[2][0])
        self.assertIn(self.popular_proposal3, response.context['popular_proposals'])