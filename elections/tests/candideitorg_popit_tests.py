# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import CandidatePerson
from candideitorg.models import Candidate as CanCandidate, Link
from popolo.models import Person
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
