# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.core.urlresolvers import reverse
from django.forms import Form
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     ProposalTemporaryData)
from popular_proposal.filters import (ProposalWithoutAreaFilter,
                                      ProposalWithAreaFilter)
from elections.models import Area, Candidate, Election
from backend_candidate.models import Candidacy
from popular_proposal.forms import (AuthorityCommitmentForm,
                                    AuthorityNotCommitingForm,
                                    )
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from constance.test import override_config
from django.test import override_settings
from popular_proposal.tests.views_tests import PopularProposalTestCaseBase

class ProposalViewTestCase(TestCase):
    def setUp(self):
        super(ProposalViewTestCase, self).setUp()
        self.algarrobo = Area.objects.get(id='algarrobo-5602')

    def test_thanks_page(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              join_advocacy_url=u"http://whatsapp.com/mygroup",
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('popular_proposals:thanks', kwargs={'pk': temporary_data.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['proposal'], temporary_data)

class EmbeddedViewsTests(PopularProposalTestCaseBase):
    def setUp(self):
        super(EmbeddedViewsTests, self).setUp()

    def test_get_popular_proposals_per_area_embedded(self):
        url = reverse('popular_proposals:area_embedded',
                      kwargs={'slug': self.algarrobo.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['layout'], 'embedded_base.html')
        self.assertTrue(response.context['is_embedded'])
        self.assertTemplateUsed('popular_proposal/area.html')
        self.assertTemplateUsed('embedded_base.html')
        self.assertIsInstance(response.context['form'], Form)
        self.assertIn(self.popular_proposal1,
                      response.context['popular_proposals'])
        self.assertIn(self.popular_proposal2,
                      response.context['popular_proposals'])
        self.assertNotIn(self.popular_proposal3,
                         response.context['popular_proposals'])
        response = self.client.get(url, {'clasification': TOPIC_CHOICES[2][0]})
        form = response.context['form']
        self.assertEquals(form.fields['clasification'].initial, TOPIC_CHOICES[2][0])
        self.assertNotIn(self.popular_proposal1,
                         response.context['popular_proposals'])

        self.assertIn(self.popular_proposal2,
                      response.context['popular_proposals'])