# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.models import Candidate, NON_WHITE_KEY, NON_MALE_KEY
from merepresenta.tests.volunteers import VolunteersTestCaseBase
from elections.models import PersonalData


class CandidateOrderingTests(VolunteersTestCaseBase):
	def setUp(self):
		super(CandidateOrderingTests, self).setUp()


	def test_women_have_an_extra_value(self):
		Candidate.objects.filter(id__in=[4, 5]).update(gender=NON_MALE_KEY)
		cs = Candidate.objects.filter(id__in=[4,5])
		self.assertEquals(cs[0].is_women, 1)
		self.assertEquals(cs[1].is_women, 1)

	def test_race_is_also_an_extra_value(self):
		c = Candidate.objects.get(id=5)
		c.race = NON_WHITE_KEY["possible_values"][0]
		c.save()
		
		cs = Candidate.objects.filter(id__in=[c.id])
		self.assertEquals(cs[0].is_non_white, 1)

	def test_email_repeated_is_also_an_extra_value(self):
		c = Candidate.objects.get(id=5)
		c.email_repeated = True
		c.save()
		
		cs = Candidate.objects.filter(id__in=[c.id])
		self.assertEquals(cs[0].bad_email, 1)
		self.assertEquals(Candidate.objects.get(id=5).desprivilegio, 1)

	def test_bad_email_is_also_an_extra_value(self):
		c = Candidate.objects.get(id=5)
		c.original_email = ''
		c.save()
		
		cs = Candidate.objects.filter(id__in=[c.id])
		self.assertEquals(cs[0].bad_email, 1)
		self.assertEquals(Candidate.objects.get(id=5).desprivilegio, 1)

		c.original_email = None
		c.save()
		cs = Candidate.objects.filter(id__in=[c.id])
		self.assertEquals(cs[0].bad_email, 1)
		self.assertEquals(Candidate.objects.get(id=5).desprivilegio, 1)

	def test_it_sums_values(self):
		self.set_desprivilegios_on_candidates()
		#NO EMAILS DESPRIVILEGIO SUMS UP
		
		self.assertEquals(Candidate.objects.get(id=5).desprivilegio, 3)
		self.assertEquals(Candidate.objects.get(id=4).desprivilegio, 2)
		
		cs = Candidate.objects.all().order_by('-desprivilegio')
		self.assertEquals(int(cs[0].id), 5)
		self.assertEquals(int(cs[1].id), 4)

	def test_lgbt_adds_one(self):
		Candidate.objects.filter(id=5).update(lgbt=True)
		self.assertEquals(Candidate.objects.get(id=5).is_lgbt, 1)
		self.assertEquals(Candidate.objects.get(id=5).desprivilegio, 2)

