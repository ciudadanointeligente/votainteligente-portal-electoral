# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election
from django.core.urlresolvers import reverse
from candideitorg.models import Candidate

class CandidateInElectionsViewsTestCase(TestCase):
	def setUp(self):
		super(CandidateInElectionsViewsTestCase, self).setUp()
		self.tarapaca = Election.objects.get(id=1)
		self.coquimbo = Election.objects.get(id=2)

	def test_url_candidate(self):
		url = reverse('candidate_detail_view', kwargs={
			'election_slug':self.tarapaca.slug,
			'slug':self.tarapaca.can_election.candidate_set.all()[0].slug
			})
		
		self.assertTrue(url)

	def test_url_duplicated(self):
		candidate = self.coquimbo.can_election.candidate_set.all()[0]
		candidate.slug = self.tarapaca.can_election.candidate_set.all()[0].slug
		candidate.save()

		url_2 = reverse('candidate_detail_view', kwargs={
			'election_slug':self.coquimbo.slug,
			'slug':self.coquimbo.can_election.candidate_set.all()[0].slug
			})

		response = self.client.get(url_2)
		self.assertEquals(response.status_code, 200)
		self.assertEqual(response.context['election'], self.coquimbo)
		self.assertEqual(response.context['candidate'], candidate)
	
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
		self.antofa = Election.objects.get(id=1)

	def test_url_better_half(self):
		url = reverse('soul_mate_detail_view', 
			kwargs={
			'slug':self.antofa.slug
			})
		self.assertTrue(url)

	def test_url_is_reachable_for_better_half(self):
		url = reverse('soul_mate_detail_view', 
			kwargs={
			'slug':self.antofa.slug,
			})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertIn("election", response.context)
		self.assertEquals(response.context["election"], self.antofa)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'elections/soulmate_candidate.html')

	def test_post_with_data_from_html(self):

		data = {
			"importance-0": "3",
			"importance-1": "3",
			"importance-2": "3",
			"question-0": "8",
			"question-1": "11",
			"question-2": "14",
			"question-id-0": "4",
			"question-id-1": "5",
			"question-id-2": "6"
		}
		url = reverse('soul_mate_detail_view', 
			kwargs={
			'slug':self.antofa.slug,
			})

		response = self.client.post(url, data=data)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed("elections/soulmate_response.html")
		self.assertIn("election", response.context)
		self.assertEquals(response.context["election"], self.antofa)
		self.assertIn("winner",response.context)
		self.assertIn("candidate", response.context["winner"])
		self.assertIsInstance(response.context["winner"]["candidate"], Candidate)
		self.assertIn("others",response.context)

		candidatos_antofa = self.antofa.can_election.candidate_set.all()
		self.assertIn(response.context["winner"]["candidate"], candidatos_antofa)

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