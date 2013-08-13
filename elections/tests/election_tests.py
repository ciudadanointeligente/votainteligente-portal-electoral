from django.test import TestCase
from elections.models import Election
from django.db import IntegrityError
from loremipsum import get_paragraphs


class ElectionTestCase(TestCase):
	def setUp(self):
		super(ElectionTestCase, self).setUp()

	def test_election_create(self):
		election = Election.objects.create(
			name='the name',
			slug='the-slug',
			description='this is a description'
			)
		self.assertEquals(election.name, 'the name')
		self.assertEquals(election.slug, 'the-slug')
		self.assertEquals(election.description, 'this is a description')

	def test_there_are_no_two_elections_with_the_same_slug(self):
		election1 = Election.objects.create(
			slug='the-slug',
			)
		election2 = Election.objects.create(
				slug='the-slug',
				)
		self.assertNotEquals(election1.slug, election2.slug)


	def test_slug_based_on_the_name(self):
		election = Election.objects.create(
			name='the name'
			)
		self.assertEquals(election.slug, 'the-name')


	def test_description_is_very_long(self):
		paragraphs = get_paragraphs(25)
		lorem_ipsum = ', '.join(paragraphs)
		election = Election.objects.create(
			name='the name',
			description=lorem_ipsum
			)
		self.assertEquals(election.description, lorem_ipsum)


