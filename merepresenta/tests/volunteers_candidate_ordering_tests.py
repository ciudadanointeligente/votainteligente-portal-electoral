# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.models import Candidate
from elections.tests import VotaInteligenteTestCase as TestCase


class CandidateOrderingTests(TestCase):
	def setUp(self):
		super(CandidateOrderingTests, self).setUp()


	def test_women_have_an_extra_value(self):
		Candidate.objects.filter(id__in=[4, 5]).update(gender='F')
		cs = Candidate.objects.filter(id__in=[4,5])
		self.assertEquals(cs[0].is_women, 1)
		self.assertEquals(cs[1].is_women, 1)


