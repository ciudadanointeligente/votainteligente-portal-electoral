# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import CandidatePerson, Election
from candideitorg.models import Candidate as CanCandidate, Election as CanElection
from django.utils.unittest import skip
from popit.models import Person


class CandideitorCandideitPopitPerson(TestCase):
    def setUp(self):
        super(CandideitorCandideitPopitPerson, self).setUp()
        self.pedro = Person.objects.get(name="Pedro")
        self.marcel = Person.objects.get(name="Marcel")
        self.candidato1 = CanCandidate.objects.get(id=1)
        self.candidato2 = CanCandidate.objects.get(id=2)

    def test_create_a_model_that_relates_them_both(self):
        candidate_person = CandidatePerson.objects.create(
            person=self.pedro,
            candidate=self.candidato1
            )

        self.assertEquals(candidate_person.person, self.pedro)
        self.assertEquals(candidate_person.candidate, self.candidato1)

        self.assertEquals(self.pedro.relation, candidate_person)
        self.assertEquals(self.candidato1.relation, candidate_person)

    @skip('automatic creation of elections before creation of candidates.')
    def test_when_creating_a_candidate_it_creates_a_person(self):
        the_election = self.candidato1.election

        #We have to think that
        can_candidate = CanCandidate.objects.create(
            remote_id=1,
            resource_uri="/api/v2/candidate/1/",
            name="Perico los Palotes",
            election=the_election.can_election
            )

        self.assertIsNotNone(can_candidate.relation)
        self.assertEquals(can_candidate.relation.person.name, can_candidate.name)


class AutomaticCreationOfThingsWhenLoadingCandideitorgs(TestCase):
    #Ya se que esto está terrible de mal escrito por que no describe niuna wea
    #pero la idea es que cuando se cree una elección del candideitorg, que viene desde 
    #el django candideitorg se creen elecciones del votainteligente
    #y además se cree un popit API instance
    #Si a alguien se le ocurre un mejor nombre que lo cambie!
    def setUp(self):
        super(AutomaticCreationOfThingsWhenLoadingCandideitorgs, self).setUp()


    def test_it_creates_an_election_out_of_a_candideitorg_election(self):
        can_election = CanElection.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )
        election = Election.objects.get(can_election=can_election)
        
        self.assertIsNotNone(election)
        self.assertEquals(election.name, can_election.name)
        self.assertEquals(election.description, can_election.description)

#It should create only one election per can_election but I don't know how to write this test
#yet
    #def test_it_creates_a_popit_API_client(self):
