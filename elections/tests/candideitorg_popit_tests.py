# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
#from elections.models import CandidatePerson
from candideitorg.models import Candidate as CanCandidate, Link
from popolo.models import Person
from django.template.loader import get_template
from django.template import Context, Template
from unittest import skip


@skip("por ahor")
class CandideitorCandideitPopitPerson(TestCase):
    def setUp(self):
        super(CandideitorCandideitPopitPerson, self).setUp()
        self.pedro = Person.objects.get(id=1)
        self.marcel = Person.objects.get(id=2)
        self.candidato1 = CanCandidate.objects.get(id=1)
        self.candidato2 = CanCandidate.objects.get(id=2)

    def test_realtion_stores_extra_atributes(self):
        candidate_person = CandidatePerson.objects.get(
            person=self.pedro,
            candidate=self.candidato1
            )
        #Deletes created relation
        candidate_person.delete()
        candidate_person = CandidatePerson.objects.create(
            person=self.pedro,
            candidate=self.candidato1,
            portrait_photo='http://imgur.com/0tJAgHo',
            custom_ribbon='ribbon text'
            )

        self.assertEquals(candidate_person.person, self.pedro)
        self.assertEquals(candidate_person.candidate, self.candidato1)

        self.assertEquals(self.pedro.relation, candidate_person)
        self.assertEquals(self.candidato1.relation, candidate_person)
        self.assertFalse(candidate_person.reachable)
        self.assertFalse(candidate_person.description)
        self.assertEquals(candidate_person.portrait_photo, 'http://imgur.com/0tJAgHo')
        # self.assertTrue(False)
