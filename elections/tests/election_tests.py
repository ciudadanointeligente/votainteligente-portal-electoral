from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election
from django.db import IntegrityError
from loremipsum import get_paragraphs
from django.core.urlresolvers import reverse


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
		self.assertTrue(election.searchable)
		self.assertFalse(election.highlighted)

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


	def test_has_tags(self):
		
		election = Election.objects.create(
			name='Distrito'
			)
		election.tags.add('providencia','valdivia')
		tags = [tag.name for tag in election.tags.all()]

		self.assertIn('providencia', tags)
		self.assertIn('valdivia', tags)

	def test_unicode(self):
		election = Election.objects.create(
			name='Distrito'
			)

		self.assertEquals(election.__unicode__(), election.name)

class ElectionViewTestCase(TestCase):
	def setUp(self):
		super(ElectionViewTestCase, self).setUp()
		self.election = Election.objects.filter(searchable=True)[0]

	def test_url_is_reachable(self):
		url = reverse('election_view', kwargs={'slug':self.election.slug})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)





