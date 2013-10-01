from django.test import TestCase
from django_nose import FastFixtureTestCase
from django.core.management import call_command

class VotaInteligenteTestCase(TestCase):
	fixtures = ['example_data_mini.yaml']


	def setUp(self):

		super(VotaInteligenteTestCase, self).setUp()

	def teardown_databases(self, *args, **kwargs):
		if not _reusing_db():
			return super(NoseTestSuiteRunner, self).teardown_databases(*args, **kwargs)
