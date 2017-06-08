# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.core.urlresolvers import reverse
from popular_proposal.models import PopularProposal, Commitment, ProposalTemporaryData
from popular_proposal.forms import ProposalFilterForm, ProposalAreaFilterForm
from popular_proposal.filters import ProposalAreaFilter
from elections.models import Area, Candidate
from backend_candidate.models import Candidacy
from popular_proposal.forms import (CandidateCommitmentForm,
                                    CandidateNotCommitingForm,
                                    )
from django.test import override_settings
from constance.test import override_config

class PopularProposalTestCaseBase(TestCase):
    def setUp(self):
        super(PopularProposalTestCaseBase, self).setUp()
        self.algarrobo = Area.objects.get(id='algarrobo-5602')
        self.popular_proposal1 = PopularProposal.objects.create(proposer=self.fiera,
                                                                area=self.algarrobo,
                                                                data=self.data,
                                                                clasification=u'education',
                                                                title=u'This is a title'
                                                                )
        data2 = self.data
        self.popular_proposal2 = PopularProposal.objects.create(proposer=self.fiera,
                                                                area=self.algarrobo,
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
        self.algarrobo = Area.objects.get(id='algarrobo-5602')

    def test_there_is_a_page_for_popular_proposal(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.algarrobo,
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
                                                          area=self.algarrobo,
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
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              join_advocacy_url=u"http://whatsapp.com/mygroup",
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('popular_proposals:thanks', kwargs={'pk': temporary_data.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['proposal'], temporary_data)


class ProposalHomeTestCase(PopularProposalTestCaseBase):
    def setUp(self):
        super(ProposalHomeTestCase, self).setUp()
        self.url = reverse('popular_proposals:home')

    def test_there_is_a_page(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'popular_proposal/home.html')

    @override_config(HIDDEN_AREAS="argentina")
    def test_not_showing_proposals_for_hidden_areas(self):
        argentina = Area.objects.create(name=u'Argentina')
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=argentina,
                                                          data=self.data,
                                                          title=u'This is a title'
                                                          )
        response = self.client.get(self.url)
        self.assertNotIn(popular_proposal, response.context['popular_proposals'])

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
        url = reverse('area', kwargs={'slug': self.algarrobo.id})
        response = self.client.get(url)
        self.assertIn(self.popular_proposal1,
                      response.context['popular_proposals'])
        self.assertIn(self.popular_proposal2,
                      response.context['popular_proposals'])

    def test_get_area_with_form(self):
        url = reverse('area', kwargs={'slug': self.algarrobo.id})
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
        proposal_filter = ProposalAreaFilter(area=self.algarrobo)

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
                      kwargs={'slug': self.algarrobo.id})
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


class CandidateCommitmentViewTestCase(PopularProposalTestCaseBase):
    def setUp(self):
        super(CandidateCommitmentViewTestCase, self).setUp()
        self.candidate = Candidate.objects.get(id=1)
        self.candidate2 = Candidate.objects.get(id=2)
        self.fiera.set_password('feroz')
        self.fiera.save()
        self.cadidacy = Candidacy.objects.create(candidate=self.candidate,
                                                 user=self.fiera)

    def test_there_is_a_commit_page(self):
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.popular_proposal1,
                                               commited=True)
        url = reverse('popular_proposals:commitment', kwargs={'candidate_slug': self.candidate.id,
                                                              'proposal_slug': self.popular_proposal1.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'popular_proposal/commitment/detail_yes.html')
        self.assertEquals(response.context['commitment'], commitment)
        commitment.delete()
        commitment_no = Commitment.objects.create(candidate=self.candidate,
                                                  proposal=self.popular_proposal1,
                                                  commited=False)
        url = reverse('popular_proposals:commitment', kwargs={'candidate_slug': self.candidate.id,
                                                              'proposal_slug': self.popular_proposal1.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'popular_proposal/commitment/detail_no.html')
        self.assertEquals(response.context['commitment'], commitment_no)

    def test_candidate_commiting_to_a_proposal_view(self):
        url = reverse('popular_proposals:commit_yes', kwargs={'proposal_pk': self.popular_proposal1.id,
                                                              'candidate_pk': self.candidate.id})
        logged_in = self.client.login(username=self.fiera.username, password='feroz')
        self.assertTrue(logged_in)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'popular_proposal/commitment/commit_yes.html')
        self.assertIsInstance(response.context['form'], CandidateCommitmentForm)
        self.assertEquals(response.context['proposal'], self.popular_proposal1)
        self.assertEquals(response.context['candidate'], self.candidate)

        response_post = self.client.post(url, {'terms_and_conditions': True})
        detail_url = reverse('popular_proposals:commitment', kwargs={'candidate_slug': self.candidate.id,
                                                                     'proposal_slug': self.popular_proposal1.slug})
        self.assertRedirects(response_post, detail_url)

    @override_config(PROPOSALS_ENABLED=False)
    def test_candidates_not_commiting(self):
        url = reverse('popular_proposals:commit_yes', kwargs={'proposal_pk': self.popular_proposal1.id,
                                                              'candidate_pk': self.candidate.id})
        logged_in = self.client.login(username=self.fiera.username, password='feroz')
        self.assertTrue(logged_in)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
        url = reverse('popular_proposals:commit_no', kwargs={'proposal_pk': self.popular_proposal1.id,
                                                             'candidate_pk': self.candidate.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_not_commiting_twice(self):
        Commitment.objects.create(candidate=self.candidate,
                                  proposal=self.popular_proposal1,
                                  commited=True)
        url = reverse('popular_proposals:commit_yes', kwargs={'proposal_pk': self.popular_proposal1.id,
                                                              'candidate_pk': self.candidate.id})
        logged_in = self.client.login(username=self.fiera.username, password='feroz')
        self.assertTrue(logged_in)
        response = self.client.get(url)
        # Already commited
        self.assertEquals(response.status_code, 404)

    def test_not_commiting_if_representing_someone_else(self):
        url = reverse('popular_proposals:commit_yes', kwargs={'proposal_pk': self.popular_proposal1.id,
                                                              'candidate_pk': self.candidate2.id})
        logged_in = self.client.login(username=self.fiera.username, password='feroz')
        self.assertTrue(logged_in)
        response = self.client.get(url)
        # Fiera has nothing to do with candidate2
        self.assertEquals(response.status_code, 404)

        # Fiera cannot commit to a promise for another area
        url = reverse('popular_proposals:commit_yes', kwargs={'proposal_pk': self.popular_proposal3.id,
                                                              'candidate_pk': self.candidate.id})
        logged_in = self.client.login(username=self.fiera.username, password='feroz')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_not_commiting_as_candidate(self):
        url = reverse('popular_proposals:commit_no', kwargs={'proposal_pk': self.popular_proposal1.id,
                                                             'candidate_pk': self.candidate.id})
        logged_in = self.client.login(username=self.fiera.username, password='feroz')
        self.assertTrue(logged_in)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'popular_proposal/commitment/commit_no.html')
        self.assertIsInstance(response.context['form'], CandidateNotCommitingForm)

        response_post = self.client.post(url, {'terms_and_conditions': True,
                                               'details': u'no me gustó pa na la propuesta'})
        detail_url = reverse('popular_proposals:commitment', kwargs={'candidate_slug': self.candidate.id,
                                                                     'proposal_slug': self.popular_proposal1.slug})
        self.assertRedirects(response_post, detail_url)
