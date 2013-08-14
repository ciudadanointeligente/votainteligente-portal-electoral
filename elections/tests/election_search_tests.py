# coding=utf-8
from django.test import TestCase
from elections.models import Election
from haystack import indexes
from elections.search_indexes import ElectionIndex
from elections.forms import ElectionForm
from haystack.forms import SearchForm
from django.core.urlresolvers import reverse

class ElectionIndexTestCase(TestCase):
	def setUp(self):
		super(ElectionIndexTestCase, self).setUp()

	def test_election_index(self):
		index = ElectionIndex()

		self.assertIsInstance(index, indexes.SearchIndex)
		self.assertIsInstance(index, indexes.Indexable)
		self.assertEquals(index.get_model(), Election)

	def test_what_is_indexed(self):
		election = Election.objects.create(name=u'XV - Araucanía Sur')
		election.tags.add(u'Nueva Imperial', u'Pitrufquén', u'Saavedra')
		index = ElectionIndex()

		indexed_election = index.text.prepare_template(election)

		self.assertIn(election.name, indexed_election)
		self.assertIn(u'Nueva Imperial', indexed_election)
		self.assertIn(u'Pitrufquén', indexed_election)
		self.assertIn(u'Saavedra', indexed_election)


class ElectionSearchFormTestCase(TestCase):
	def setUp(self):
		super(ElectionSearchFormTestCase, self).setUp()

	def test_election_form(self):
		form = ElectionForm()

		self.assertIsInstance(form, SearchForm)



class ElectionSearchViewTestCase(TestCase):
	def setUp(self):
		super(ElectionSearchViewTestCase, self).setUp()

	def test_get_url(self):
		url = reverse('search')
		response = self.client.get(url)

		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'search.html')
		self.assertTemplateUsed(response, 'base.html')
		self.assertIn('form', response.context)
		self.assertIsInstance(response.context['form'], ElectionForm)