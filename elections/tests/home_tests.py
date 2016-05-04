from elections.tests import VotaInteligenteTestCase as TestCase
from django.core.urlresolvers import reverse
from elections.views import HomeView
from elections.forms import ElectionSearchByTagsForm
from unittest import skip
from elections.models import Election
from django.contrib.auth.forms import AuthenticationForm
from registration.forms import RegistrationForm


class HomeTestCase(TestCase):
	def setUp(self):
		super(HomeTestCase, self).setUp()

	def test_get_home(self):
		url = reverse('home')
		response = self.client.get(url)
		self.assertTrue(response.status_code, 200)
		self.assertTemplateUsed(response, 'elections/home.html')
		self.assertTemplateUsed(response, 'base.html')
		self.assertIn('form',response.context)
		self.assertIsInstance(response.context['form'], ElectionSearchByTagsForm)

	def test_home_view(self):
		view = HomeView()
		context = view.get_context_data()

		self.assertIn('form', context)
		self.assertIn('featured_elections', context)
		self.assertIn('searchable_elections_enabled', context)
		self.assertTrue(context['searchable_elections_enabled'])
		self.assertIsInstance(context['form'], ElectionSearchByTagsForm)
		self.assertIn('register_new_form', context)
		self.assertIn('login_form', context)
		self.assertIsInstance(context['register_new_form'], RegistrationForm)
		self.assertIsInstance(context['login_form'], AuthenticationForm)

	def test_searchable_elections_disabled(self):
		Election.objects.all().update(searchable=False)
		view = HomeView()
		context = view.get_context_data()
		self.assertFalse(context['searchable_elections_enabled'])
