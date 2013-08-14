# coding=utf-8
from django.test import TestCase
from elections.models import Election
from haystack import indexes
from elections.search_indexes import ElectionIndex


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