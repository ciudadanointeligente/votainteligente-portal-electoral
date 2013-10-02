# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election
from django.core.management import call_command

class ElectionsTagsLoaderTestCase(TestCase):
	def setUp(self):
		super(ElectionsTagsLoaderTestCase, self).setUp()
		self.antofa = Election.objects.get(id=1)

	def test_add_tag(self):
		self.assertEquals(self.antofa.tags.all().count(), 0)
		call_command('elections_tags_loader', 'elections/tests/fixtures/elections_tags.csv', verbosity=0)
		self.assertEquals(self.antofa.tags.all().count(), 9)
		expected_existing_tags = [
															u'Antofagasta', 
															u'Calama', 
															u'María Elena', 
															u'Mejillones', 
															u'Ollagüe', 
															u'San Pedro de Atacama', 
															u'Sierra Gorda', 
															u'Taltal', 
															u'Tocopilla']
		for tag in expected_existing_tags:
			election = Election.objects.get(tags__name=tag)
			self.assertEquals(self.antofa, election)
