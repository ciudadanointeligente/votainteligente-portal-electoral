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

class QuestionaryInElectionsViewTestCase(TestCase):
	def setUp(self):
		super(QuestionaryInElectionsViewTestCase, self).setUp()
		self.tarapaca = Election.objects.get(id=1)

	def test_url_question(self):
		url = reverse('questionary_detail_view', 
			kwargs={'slug':self.tarapaca.slug})
		self.assertTrue(url)

	def test_url_is_reachable(self):
		url = reverse('questionary_detail_view', 
			kwargs={'slug':self.tarapaca.slug})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.context["election"], self.tarapaca)
		self.assertTemplateUsed(response, 'elections/election_questionary.html')

class FaceToFaceViewTestCase(TestCase):
	def setUp(self):
		super(FaceToFaceViewTestCase, self).setUp()
		self.tarapaca = Election.objects.get(id=1)

	def test_url_face_to_face_two_candidate(self):
		url = reverse('face_to_face_two_candidates_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug,
			'slug_candidate_one':self.tarapaca.can_election.candidate_set.all()[0].slug,
			'slug_candidate_two':self.tarapaca.can_election.candidate_set.all()[1].slug,
			})
		self.assertTrue(url)

	def test_url_face_to_face_one_candidate(self):
		url = reverse('face_to_face_one_candidate_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug,
			'slug_candidate_one':self.tarapaca.can_election.candidate_set.all()[0].slug
			})
		self.assertTrue(url)

	def test_url_face_to_face_no_candidate(self):
		url = reverse('face_to_face_no_candidate_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug
			})
		self.assertTrue(url)

	def test_url_is_reachable_for_two_candidates(self):
		url = reverse('face_to_face_two_candidates_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug,
			'slug_candidate_one':self.tarapaca.can_election.candidate_set.all()[0].slug,
			'slug_candidate_two':self.tarapaca.can_election.candidate_set.all()[1].slug,
			})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'elections/compare_candidates.html')
		self.assertIn('first_candidate', response.context)
		self.assertEqual(response.context['first_candidate'], self.tarapaca.can_election.candidate_set.all()[0])
		self.assertIn('second_candidate', response.context)
		self.assertEqual(response.context['second_candidate'], self.tarapaca.can_election.candidate_set.all()[1])

	def test_url_is_reachable_for_one_candidates(self):
		url = reverse('face_to_face_one_candidate_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug,
			'slug_candidate_one':self.tarapaca.can_election.candidate_set.all()[1].slug,
			})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'elections/compare_candidates.html')
		self.assertIn('first_candidate', response.context)
		self.assertEqual(response.context['first_candidate'], self.tarapaca.can_election.candidate_set.all()[1])


	def test_url_is_reachable_for_no_one_candidates(self):
		url = reverse('face_to_face_no_candidate_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug,
			})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'elections/compare_candidates.html')

class SoulMateTestCase(TestCase):
	def setUp(self):
		super(SoulMateTestCase, self).setUp()
		self.tarapaca = Election.objects.get(id=1)

	def test_url_better_half(self):
		url = reverse('soul_mate_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug
			})
		self.assertTrue(url)

	def test_url_is_reachable_for_better_half(self):
		url = reverse('soul_mate_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug,
			})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'elections/soulmate_candidate.html')

class AskTestCase(TestCase):
	def setUp(self):
		super(AskTestCase, self).setUp()
		self.tarapaca = Election.objects.get(id=1)

	def test_url_ask(self):
		url = reverse('ask_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug
			})
		self.assertTrue(url)

	def test_url_is_reachable_for_ask(self):
		url = reverse('ask_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug,
			})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'elections/ask_candidate.html')

class RankingTestCase(TestCase):
	def setUp(self):
		super(RankingTestCase, self).setUp()
		self.tarapaca = Election.objects.get(id=1)

	def test_url_ask(self):
		url = reverse('ranking_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug
			})
		self.assertTrue(url)

	def test_url_is_reachable_for_ranking(self):
		url = reverse('ranking_detail_view', 
			kwargs={
			'slug':self.tarapaca.slug,
			})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'elections/ranking_candidates.html')

class MediaNaranjaTestCase(TestCase):
	def setUp(self):
		super(MediaNaranjaTestCase, self).setUp()

	def test_get(self):
		pass

	def test_put(self):
		pass