# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election
from django.core.urlresolvers import reverse

class CandidateInElectionsViewsTestCase(TestCase):
	def setUp(self):
		super(CandidateInElectionsViewsTestCase, self).setUp()
		self.tarapaca = Election.objects.get(id=1)

	def test_url_candidate(self):
		url = reverse('candidate_detail_view', kwargs={
			'election_slug':self.tarapaca.slug,
			'slug':self.tarapaca.can_election.candidate_set.all()[0].slug
			})
		
		self.assertTrue(url)

	
	def test_url_is_reachable(self):
		url = reverse('candidate_detail_view', kwargs={
			'election_slug':self.tarapaca.slug,
			'slug':self.tarapaca.can_election.candidate_set.all()[0].slug
			})
		
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertIn('election', response.context)
		self.assertEqual(response.context['election'], self.tarapaca)
		self.assertEqual(response.context['candidate'], self.tarapaca.can_election.candidate_set.all()[0])
		self.assertTemplateUsed(response, 'elections/candidate_detail.html')
		self.assertTemplateUsed(response, 'base.html')