# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import CandidatePerson, Election
from candideitorg.models import Candidate as CanCandidate, Election as CanElection, Link
from popolo.models import Person
from django.db import IntegrityError
from django.template.loader import get_template
from django.template import Context, Template


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

    def test_it_creates_a_link_to_the_candidate_twitter(self):
        Link.objects.create(url='http://twitter.com/candidato1',
            name='twitter',
            candidate=self.candidato1,
            remote_id=1,
            resource_uri='string')
        candidate_person, created = CandidatePerson.objects.get_or_create(
            person=self.pedro,
            candidate=self.candidato1
            )
        self.assertEquals(candidate_person.twitter, 'candidato1')

    def test_it_returns_none_if_there_is_no_twitter_link(self):
        candidate_person, created = CandidatePerson.objects.get_or_create(
            person=self.pedro,
            candidate=self.candidato1
            )
        self.assertIsNone(candidate_person.twitter)

    def test_it_only_returns_one_twitter_link(self):
        Link.objects.create(url='http://twitter.com/candidato1',
            name='twitter',
            candidate=self.candidato1,
            remote_id=1,
            resource_uri='string')
        Link.objects.create(url='http://twitter.com/candidato1_twitter2',
            name='twitter',
            candidate=self.candidato1,
            remote_id=1,
            resource_uri='string')
        candidate_person, created = CandidatePerson.objects.get_or_create(
            person=self.pedro,
            candidate=self.candidato1
            )
        self.assertEquals(candidate_person.twitter, 'candidato1')

    def test_tweet_if_candidator_unanswered(self):
        Link.objects.create(url='http://twitter.com/candidato1_twitter',
            name='twitter',
            candidate=self.candidato1,
            remote_id=1,
            resource_uri='string')
        self.candidato1.has_answered = False
        self.candidato1.save()
        candidate_person, created = CandidatePerson.objects.get_or_create(
            person=self.pedro,
            candidate=self.candidato1
            )
        template_str = get_template('elections/twitter/no_candidator_answer.html')
        context = Context({
            "candidate": self.candidato1,
            "twitter": "candidato1_twitter"
            })
        expected_twitter_button = template_str.render(context)
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% no_ha_respondido_twitter_button %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": self.candidato1}))
        self.assertEquals(actual_twitter_button, expected_twitter_button)

    def test_no_tweet_if_candidate_has_no_twitter(self):
        self.candidato1.has_answered = False
        self.candidato1.save()
        candidate_person, created = CandidatePerson.objects.get_or_create(
            person=self.pedro,
            candidate=self.candidato1
            )
        expected_twitter_button = ""
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% no_ha_respondido_twitter_button %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": self.candidato1}))
        actual_twitter_button = actual_twitter_button.strip()
        self.assertEquals(actual_twitter_button, expected_twitter_button)

    def test_follow_the_conversation_in_twitter(self):
        Link.objects.create(url='http://twitter.com/candidato1_twitter',
            name='twitter',
            candidate=self.candidato1,
            remote_id=1,
            resource_uri='string')
        candidate_person, created = CandidatePerson.objects.get_or_create(
            person=self.pedro,
            candidate=self.candidato1
            )
        template_str = get_template('elections/twitter/follow_the_conversation.html')
        context = Context({
            "twitter": "candidato1_twitter",
            "candidate": self.candidato1
            })
        expected_twitter_button = template_str.render(context)
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% follow_on_twitter %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": self.candidato1}))
        self.assertEquals(actual_twitter_button, expected_twitter_button)

    def test_ranking_twitter_button(self):
        Link.objects.create(url='http://twitter.com/candidato1_twitter',
            name='twitter',
            candidate=self.candidato1,
            remote_id=1,
            resource_uri='string')
        candidate_person, created = CandidatePerson.objects.get_or_create(
            person=self.pedro,
            candidate=self.candidato1
            )
        template_str = get_template('elections/twitter/ranking_twitter.html')
        context = Context({
            "twitter": "candidato1_twitter",
            "candidate": self.candidato1,
            'btn_text': 'message button',
            'popup_text': 'message twitter window'
            })
        expected_twitter_button = template_str.render(context)
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% twitter_on_ranking 'message button' 'message twitter window' %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": self.candidato1}))
        self.assertEquals(actual_twitter_button, expected_twitter_button)

    def test_unicode(self):
        candidate_person, created = CandidatePerson.objects.get_or_create(
            person=self.pedro,
            candidate=self.candidato1
            )
        expected_unicode = 'Extra info de %(candidate)s' % {
            "candidate": self.pedro.name
        }

        self.assertEquals(expected_unicode, candidate_person.__unicode__())


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
            description="Elecciones CEI 2012",
            remote_id=1,
            information_source="",
            logo="/media/photos/dummy.jpg",
            name="cei 2012",
            resource_uri="/api/v2/election/1/",
            slug="cei-2012",
            use_default_media_naranja_option=True
            )
        election = Election.objects.get(can_election=can_election)
        self.assertIsNotNone(election)
        self.assertEquals(election.name, can_election.name)
        self.assertEquals(election.description, can_election.description)

    #ya se me ocurrió wn!!
    def test_it_only_creates_one(self):
        can_election = CanElection.objects.create(
            description="Elecciones CEI 2012",
            remote_id=1,
            information_source="",
            logo="/media/photos/dummy.jpg",
            name="cei 2012",
            resource_uri="/api/v2/election/1/",
            slug="cei-2012",
            use_default_media_naranja_option=True
            )
        can_election.save()

        self.assertEquals(Election.objects.filter(can_election=can_election).count(), 1)

        election = Election.objects.get(can_election=can_election)
        self.assertTrue(election)

    def test_can_election_to_election_is_one_to_one(self):
        can_election = CanElection.objects.create(
            description="Elecciones CEI 2012",
            remote_id=1,
            information_source="",
            logo="/media/photos/dummy.jpg",
            name="cei 2012",
            resource_uri="/api/v2/election/1/",
            slug="cei-2012",
            use_default_media_naranja_option=True
            )

        #ok it now has a relation between a can_election and an election
        #if I try add another one it should simply throw an integrity error

        with self.assertRaises(IntegrityError):
            Election.objects.create(description=can_election.description,
                    can_election=can_election,
                    name=can_election.name)

    def test_election_can_election_related_name(self):
        can_election = CanElection.objects.create(
            description="Elecciones CEI 2012",
            remote_id=1,
            information_source="",
            logo="/media/photos/dummy.jpg",
            name="cei 2012",
            resource_uri="/api/v2/election/1/",
            slug="cei-2012",
            use_default_media_naranja_option=True
            )

        election = Election.objects.get(can_election=can_election)
        self.assertEquals(can_election.election, election)
