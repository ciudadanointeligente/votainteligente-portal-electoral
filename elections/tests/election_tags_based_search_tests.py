# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django import forms
from django.utils.unittest import skip
from django.core.urlresolvers import reverse
from elections.forms import ElectionSearchByTagsForm
from elections.views import ElectionsSearchByTagView
from django.views.generic.edit import FormView
from django.utils.translation import ugettext as _
from elections.models import Election

class ElectionTagsBasedSearchViewTestCase(TestCase):
	def setUp(self):
		super(ElectionTagsBasedSearchViewTestCase, self).setUp()

	#@skip('missing view')
	def test_get_url(self):
		url = reverse('tags_search')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'search/tags_search.html')
		self.assertIn('form', response.context)
		self.assertIsInstance(response.context['form'], forms.Form)
		self.assertIsInstance(response.context['form'], ElectionSearchByTagsForm)


	def test_tags_search_view_params(self):
		view = ElectionsSearchByTagView()
		self.assertIsInstance(view, FormView)
		self.assertEquals(view.get_success_url(), reverse('tags_search'))
		self.assertEquals(view.form_class, ElectionSearchByTagsForm)
		self.assertEquals(view.template_name, 'search/tags_search.html')

	def test_get_result(self):
		url = reverse('tags_search')
		camina = u'Camiña'
		data = {
		'q':camina
		}
		response = self.client.get(url, data=data)
		self.assertIn('result', response.context)
		expected_result = Election.objects.filter(tags__name__in=[camina])

		self.assertQuerysetEqual(response.context['result'], [repr(r) for r in expected_result])

class ElectionSearchByTagsFormTestCase(TestCase):
	def setUp(self):
		super(ElectionSearchByTagsFormTestCase, self).setUp()

	def test_it_has_a_field_named_q(self):
		form = ElectionSearchByTagsForm()

		self.assertIn('q', form.fields)
		self.assertIsInstance(form.fields['q'], forms.CharField)
		self.assertFalse(form.fields['q'].required)
		self.assertEquals(form.fields['q'].label, _('Busca tu comuna'))

	def test_get_result(self):
		camina = u"Camiña"
		expected_result = Election.objects.filter(tags__name__in=[camina])
		initial = {
			'q':camina
		}
		form = ElectionSearchByTagsForm(data=initial)
		#the view does this for me
		form.full_clean()
		#the view does this for me
		
		search_result = form.get_search_result()
		self.assertQuerysetEqual(search_result, [repr(r) for r in expected_result])