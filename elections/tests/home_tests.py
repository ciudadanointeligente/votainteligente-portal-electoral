from django.test import TestCase
from django.core.urlresolvers import reverse
from elections.views import HomeView
from elections.forms import ElectionSearchByTagsForm
from django.utils.unittest import skip

class HomeTestCase(TestCase):
	def setUp(self):
		super(HomeTestCase, self).setUp()

	def test_url_ask_them(self):
		url = reverse('election_ask_them')
		self.assertTrue(url)
		# response = self.client.get(url)
		# self.assertTrue(response.status_code, 200)
		# self.assertTemplateUsed(response, 'elections/home.html')
		# self.assertTemplateUsed(response, 'base.html')
		# self.assertIn('form',response.context)
		# self.assertIsInstance(response.context['form'], ElectionSearchByTagsForm)

