# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.test.utils import override_settings
from elections.models import CandidatePerson, Election
from candideitorg.models import Candidate as CanCandidate, Election as CanElection
from django.utils.unittest import skip
from popit.models import Person, ApiInstance as PopitApiInstance
from django.db import IntegrityError
from django.conf import settings
import simplejson as json
from writeit.models import WriteItInstance, WriteItApiInstance
import urllib
import re
from popit.tests.instance_helpers import delete_api_database, get_api_database_name, get_api_client

from candideitorg.models import election_finished


class CandideitorCandideitPopitPerson(TestCase):
    def setUp(self):
        super(CandideitorCandideitPopitPerson, self).setUp()
        self.pedro = Person.objects.get(id=1)
        self.marcel = Person.objects.get(id=2)
        self.candidato1 = CanCandidate.objects.get(id=1)
        self.candidato2 = CanCandidate.objects.get(id=2)

    def test_create_a_model_that_relates_them_both(self):
        candidate_person, created = CandidatePerson.objects.get_or_create(
            person=self.pedro,
            candidate=self.candidato1
            )

        self.assertEquals(candidate_person.person, self.pedro)
        self.assertEquals(candidate_person.candidate, self.candidato1)

        self.assertEquals(self.pedro.relation, candidate_person)
        self.assertEquals(self.candidato1.relation, candidate_person)



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

    #ya se me ocurrió wn!!
    def test_it_only_creates_one(self):
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
        can_election.save()

        self.assertEquals(Election.objects.filter(can_election=can_election).count(), 1)

        election = Election.objects.get(can_election=can_election)
        self.assertTrue(election)

    def test_can_election_to_election_is_one_to_one(self):
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

        #ok it now has a relation between a can_election and an election
        #if I try add another one it should simply throw an integrity error

        with self.assertRaises(IntegrityError) as e:
            Election.objects.create(
                    description = can_election.description,
                    can_election=can_election,
                    name = can_election.name,
                    )


    def test_election_can_election_related_name(self):
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
        self.assertEquals(can_election.election, election)

    def test_it_creates_a_popit_API_client(self):
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
        #Create one ApiInstance for the love of the FSM

        self.assertIsNotNone(can_election.election.popit_api_instance)
        #manso webeo pa llegar a la APIinstance

        api_instance = can_election.election.popit_api_instance

        short_slug = hex(hash(can_election.election.slug))

        expected_url = settings.POPIT_API_URL % ( short_slug )
        self.assertEquals(api_instance.url, expected_url)


class AutomaticCreationOfAPopitPerson(TestCase):
    def setUp(self):
        super(AutomaticCreationOfAPopitPerson, self).setUp()
        self.can_election = CanElection.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )

    def tearDown(self):
        super(AutomaticCreationOfAPopitPerson, self).tearDown()
        delete_api_database()


    def test_when_creating_a_candidate_it_creates_a_person(self):
        can_candidate = CanCandidate.objects.create(
            remote_id=1,
            resource_uri="/api/v2/candidate/1/",
            name="Perico los Palotes",
            election=self.can_election
            )

        self.assertIsNotNone(can_candidate.relation)
        self.assertEquals(can_candidate.relation.person.name, can_candidate.name)
        self.assertEquals(can_candidate.relation.person.api_instance.election, self.can_election.election)


    def test_it_does_not_create_two_relations(self):
        can_candidate = CanCandidate.objects.create(
            remote_id=1,
            resource_uri="/api/v2/candidate/1/",
            name="Perico los Palotes",
            election=self.can_election
            )
        can_candidate.save()

        self.assertTrue(can_candidate.relation)

    def test_it_posts_to_the_popit_api(self):
        

        can_candidate = CanCandidate.objects.create(
            remote_id=1,
            resource_uri="/api/v2/candidate/1/",
            name="Perico los Palotes",
            election=self.can_election
            )

        person = can_candidate.relation.person
        instance = person.api_instance
        my_re = re.compile(instance.url + "/persons/([^/]+)/{0,1}")
        self.assertIsNotNone(my_re.match(person.popit_url))

        person_id = my_re.match(person.popit_url).groups()[0]
        response = urllib.urlopen(person.popit_url)
        self.assertEquals(response.code, 200)
        response_as_json = json.loads(response.read())

    @override_settings(USE_POPIT=False)
    def test_if_there_is_a_setting_that_says_dont_use_popit_then_dont(self):
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
        can_candidate = CanCandidate.objects.create(
            remote_id=1,
            resource_uri="/api/v2/candidate/1/",
            name="Perico los Palotes",
            election=can_election
            )
        with self.assertRaises(CandidatePerson.DoesNotExist) as e:
            can_candidate.relation
        self.assertFalse(Person.objects.filter(name=can_candidate.name).exists())
        election_finished.send(sender=CanElection, instance=can_election, created=True)

        #Don't create a writeit instance either

        election = Election.objects.get(can_election=can_election)
        self.assertIsNone(election.popit_api_instance)
        self.assertIsNone(election.writeitinstance)




import uuid 
class AutomaticCreationOfAWriteitInstance(TestCase):
    def setUp(self):
        super(AutomaticCreationOfAWriteitInstance, self).setUp()
        delete_api_database()

    def tearDown(self):
        super(AutomaticCreationOfAWriteitInstance, self).tearDown()
        delete_api_database()


    def test_it_creates_an_api_instance_from_settings(self):
        from elections.models import get_current_writeit_api_instance

        instance = get_current_writeit_api_instance()

        self.assertIsInstance(instance, WriteItApiInstance)
        self.assertEquals(instance.url, settings.WRITEIT_API_URL)

    #@skip("creating api instances automatically")
    def test_it_creates_a_writeit_instance(self):
        #WriteitInstance.objects.get()
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
        self.assertIsNotNone(election.writeitinstance)
        self.assertIsInstance(election.writeitinstance, WriteItInstance)
        self.assertTrue(election.writeitinstance.name)
        self.assertEquals(election.writeitinstance.name, can_election.name)

        self.assertFalse(election.writeitinstance.url)
        self.assertFalse(election.writeitinstance.remote_id)
    

    def test_it_creates_the_writeit_instance_with_the_popit_api(self):
        name_and_slug = uuid.uuid1().hex
        can_election = CanElection.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = name_and_slug,
            resource_uri = "/api/v2/election/1/",
            slug = name_and_slug,
            use_default_media_naranja_option = True
            )
        can_candidate = CanCandidate.objects.create(
            remote_id=1,
            resource_uri="/api/v2/candidate/1/",
            name="Perico los Palotes",
            election=can_election
            )
        #print get_api_client().__getattr__('').get()['info']['databaseName']

        person = can_candidate.relation.person
        #print Person.objects.filter(api_instance = election.popit_api_instance)
        election_finished.send(sender=CanElection, instance=can_election, created=True)

        election = Election.objects.get(can_election=can_election)
        writeitinstance = election.writeitinstance
        self.assertTrue(writeitinstance.url)
        self.assertTrue(writeitinstance.remote_id)

        response = writeitinstance.api_instance.get_api().instance(writeitinstance.remote_id).get()
        persons = response['persons']
        self.assertEquals(len(persons), Person.objects.filter(api_instance = election.popit_api_instance).count())

        self.assertIn(person.popit_url, persons)


    @override_settings(USE_WRITEIT=False)
    def test_if_there_is_a_dont_use_writeit_setting_then_dont(self):
        name_and_slug = uuid.uuid1().hex
        can_election = CanElection.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = name_and_slug,
            resource_uri = "/api/v2/election/1/",
            slug = name_and_slug,
            use_default_media_naranja_option = True
            )
        can_candidate = CanCandidate.objects.create(
            remote_id=1,
            resource_uri="/api/v2/candidate/1/",
            name="Perico los Palotes",
            election=can_election
            )
        election_finished.send(sender=CanElection, instance=can_election, created=True)

        election = Election.objects.get(can_election=can_election)
        self.assertIsNone(election.writeitinstance)


