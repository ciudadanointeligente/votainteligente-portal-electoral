from django.test import TestCase
from elections.models import Election
from django.db import IntegrityError


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
		Election.objects.create(
			slug='the-slug',
			)
		with self.assertRaises(IntegrityError):
			Election.objects.create(
				slug='the-slug',
				)


	def test_slug_based_on_the_name(self):
		election = Election.objects.create(
			name='the name'
			)
		self.assertEquals(election.slug, 'the-name')


