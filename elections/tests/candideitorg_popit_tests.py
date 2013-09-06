# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import CandidatePerson
from candideitorg.models import Candidate as CanCandidate
from django.utils.unittest import skip
from popit.models import Person


class CandideitorCandideitPopitPerson(TestCase):
    def setUp(self):
        super(CandideitorCandideitPopitPerson, self).setUp()
        self.pedro = Person.objects.get(name="Pedro")
        self.marcel = Person.objects.get(name="Marcel")
        self.candidato1 = CanCandidate.objects.get(id=1)
        self.candidato2 = CanCandidate.objects.get(id=2)

    #@skip("need to import a popit person first")
    def test_create_a_model_that_relates_them_both(self):
        candidate_person = CandidatePerson.objects.create(
            person=self.pedro,
            candidate=self.candidato1
            )

        self.assertEquals(candidate_person.person, self.pedro)
        self.assertEquals(candidate_person.candidate, self.candidato1)

        self.assertEquals(self.pedro.relation, candidate_person)
        self.assertEquals(self.candidato1.relation, candidate_person)


        

