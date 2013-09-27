from elections.tests import VotaInteligenteTestCase as TestCase
from django.core.urlresolvers import reverse
from elections.models import Election


class AskTestCase(TestCase):
	def setUp(self):
		super(AskTestCase, self).setUp()
		self.election = Election.objects.all()[0]

	def test_url_ask(self):
		url = reverse('ask_detail_view', 
			kwargs={
			'slug':self.election.slug
			})
		self.assertTrue(url)

	def test_url_is_reachable_for_ask(self):
		url = reverse('ask_detail_view', 
			kwargs={
			'slug':self.election.slug,
			})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'elections/ask_candidate.html')