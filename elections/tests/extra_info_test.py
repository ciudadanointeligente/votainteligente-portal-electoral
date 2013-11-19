# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election
from django.core.management import call_command

class ExtraInfoTestCase(TestCase):
	def setUp(self):
		super(ExtraInfoTestCase, self).setUp()
		self.election = Election.objects.get(id=1)

	def test_add_extrainfo(self):
		self.assertEquals(self.election.extra_info_title, None)
		call_command('extra_info_loader', 'elections/tests/fixtures/extrainfo.csv', verbosity=0)
		self.election.extra_info_title = 'Información Municipal'
		self.assertEquals(self.election.extra_info_title, 'Información Municipal')
