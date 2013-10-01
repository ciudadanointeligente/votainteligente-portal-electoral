from django.test import TestCase
from django_nose import FastFixtureTestCase
from django.core.management import call_command

class VotaInteligenteTestCase(TestCase):
    def setUp(self):
        super(VotaInteligenteTestCase, self).setUp()
        call_command('loaddata', 'example_data_mini', verbosity=0)