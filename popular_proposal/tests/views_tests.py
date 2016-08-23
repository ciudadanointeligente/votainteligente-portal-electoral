# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.core.urlresolvers import reverse
from popular_proposal.models import PopularProposal
from popular_proposal.forms import ProposalFilterForm, ProposalAreaFilterForm
from popular_proposal.filters import ProposalAreaFilter


class PopularProposalTestCaseBase(TestCase):
    def setUp(self):
        super(PopularProposalTestCaseBase, self).setUp()
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
                                                                clasification=u'deporte',
                                                                title=u'This is a title'
                                                                )
        self.popular_proposal3 = PopularProposal.objects.create(proposer=self.fiera,
                                                                area=self.alhue,
                                        
                                                                data=data2,
                                                                clasification=u'deporte',
                                                                title=u'This is a title'
                                                                )


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

    def test_embedded_detail_popular_proposal(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
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

    def test_thanks_page(self):
        url = reverse('popular_proposals:thanks', kwargs={'pk': self.arica.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['area'], self.arica)


class ProposalHomeTestCase(PopularProposalTestCaseBase):
    def setUp(self):
        super(ProposalHomeTestCase, self).setUp()
        self.url = reverse('popular_proposals:home')

    def test_there_is_a_page(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'popular_proposal/home.html')

    def test_brings_a_list_of_proposals(self):
        response = self.client.get(self.url, {'clasification': '', 'area': ''})
        self.assertIsInstance(response.context['form'], ProposalFilterForm)

        self.assertIn(self.popular_proposal1, response.context['popular_proposals'])

        self.assertIn(self.popular_proposal2, response.context['popular_proposals'])

        response = self.client.get(self.url, {'clasification': 'deporte', 'area': ''})
        form = response.context['form']
        self.assertEquals(form.fields['clasification'].initial, 'deporte')
        self.assertNotIn(self.popular_proposal1, response.context['popular_proposals'])

        self.assertIn(self.popular_proposal2, response.context['popular_proposals'])

        response = self.client.get(self.url, {'clasification': 'deporte', 'area': self.alhue.id})
        form = response.context['form']
        self.assertEquals(form.fields['clasification'].initial, 'deporte')
        self.assertEquals(form.fields['area'].initial, self.alhue.id)
        self.assertIn(self.popular_proposal3, response.context['popular_proposals'])
        self.assertNotIn(self.popular_proposal2, response.context['popular_proposals'])
        self.assertNotIn(self.popular_proposal1, response.context['popular_proposals'])

    def test_filtering_form(self):
        data = {'clasification': '', 'area': ''}
        form = ProposalFilterForm(data=data)
        self.assertTrue(form.is_valid())

    def test_filtering_form_by_area(self):
        data = {'clasification': ''}
        form = ProposalAreaFilterForm(data=data, area=self.alhue)
        self.assertTrue(form.is_valid())

    def test_area_detail_view_brings_proposals(self):
        url = reverse('area', kwargs={'slug': self.arica.id})
        response = self.client.get(url)
        self.assertIn(self.popular_proposal1,
                      response.context['popular_proposals'])
        self.assertIn(self.popular_proposal2,
                      response.context['popular_proposals'])

    def test_get_area_with_form(self):
        url = reverse('area', kwargs={'slug': self.arica.id})
        response = self.client.get(url, {'clasification': ''})
        self.assertIsInstance(response.context['proposal_filter_form'],
                              ProposalAreaFilterForm)
        self.assertIn(self.popular_proposal1,
                      response.context['popular_proposals'])

        self.assertIn(self.popular_proposal2,
                      response.context['popular_proposals'])
        response = self.client.get(url, {'clasification': 'deporte'})
        form = response.context['proposal_filter_form']
        self.assertEquals(form.fields['clasification'].initial, 'deporte')
        self.assertNotIn(self.popular_proposal1,
                         response.context['popular_proposals'])

        self.assertIn(self.popular_proposal2,
                      response.context['popular_proposals'])


class ProposalFilterTestsCase(PopularProposalTestCaseBase):
    def setUp(self):
        super(ProposalFilterTestsCase, self).setUp()

    def test_filter_by_area(self):
        proposal_filter = ProposalAreaFilter(area=self.arica)

        self.assertIn(self.popular_proposal1, proposal_filter.qs)
        self.assertIn(self.popular_proposal2, proposal_filter.qs)
        self.assertNotIn(self.popular_proposal3, proposal_filter.qs)


class EmbeddedViewsTests(PopularProposalTestCaseBase):
    def setUp(self):
        super(EmbeddedViewsTests, self).setUp()

    def test_get_home_view(self):
        url = reverse('popular_proposals:embedded_home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'popular_proposal/home.html')
        self.assertTemplateUsed(response, 'embedded_base.html')
        self.assertIsInstance(response.context['form'], ProposalFilterForm)
        self.assertTrue(response.context['is_embedded'])

    def test_get_popular_proposals_per_area_embedded(self):
        url = reverse('popular_proposals:area_embedded',
                      kwargs={'slug': self.arica.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['layout'], 'embedded_base.html')
        self.assertTrue(response.context['is_embedded'])
        self.assertTemplateUsed('popular_proposal/area.html')
        self.assertTemplateUsed('embedded_base.html')
        self.assertIsInstance(response.context['form'], ProposalAreaFilterForm)
        self.assertIn(self.popular_proposal1,
                      response.context['popular_proposals'])
        self.assertIn(self.popular_proposal2,
                      response.context['popular_proposals'])
        self.assertNotIn(self.popular_proposal3,
                         response.context['popular_proposals'])
        response = self.client.get(url, {'clasification': 'deporte'})
        form = response.context['form']
        self.assertEquals(form.fields['clasification'].initial, 'deporte')
        self.assertNotIn(self.popular_proposal1,
                         response.context['popular_proposals'])

        self.assertIn(self.popular_proposal2,
                      response.context['popular_proposals'])