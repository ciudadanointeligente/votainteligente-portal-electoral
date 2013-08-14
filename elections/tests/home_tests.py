from django.test import TestCase
from django.core.urlresolvers import reverse

class HomeTestCase(TestCase):
	def setUp(self):
		super(HomeTestCase, self).setUp()


	def test_get_home(self):
		url = reverse('home')
		response = self.client.get(url)
		self.assertTrue(response.status_code, 200)
		self.assertTemplateUsed(response, 'elections/home.html')
		self.assertTemplateUsed(response, 'base.html')