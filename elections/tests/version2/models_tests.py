# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Person
from elections.models import Candidate, Election, QuestionCategory
from candidator.models import Category
from django.template.loader import get_template
from django.template import Context, Template


class Version2TestCase(TestCase):
    def setUp(self):
        super(Version2TestCase, self).setUp()
        self.election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            extra_info_content=u'Más Información')


class CandidaTeTestCase(Version2TestCase):
    def setUp(self):
        super(CandidaTeTestCase, self).setUp()

    def test_instanciate(self):
        candidate = Candidate.objects.create(name="Felipe Feroz",
                                             election=self.election
                                             )
        self.assertIsInstance(candidate, Person)

    def test_it_creates_a_link_to_the_candidate_twitter(self):
        candidate = Candidate.objects.get(id=1)
        candidate.links.create(url="http://twitter.com/candidato1")
        self.assertEquals(candidate.twitter, 'candidato1')

    def test_it_returns_none_if_there_is_no_twitter_link(self):
        candidate = Candidate.objects.get(id=1)
        self.assertIsNone(candidate.twitter)

    def test_it_only_returns_one_twitter_link(self):
        candidate = Candidate.objects.get(id=1)
        candidate.links.create(url="http://twitter.com/candidato1")
        candidate.links.create(url='http://twitter.com/candidato1_twitter2')

        self.assertEquals(candidate.twitter, 'candidato1')

    def test_tweet_if_candidator_unanswered(self):
        candidate = Candidate.objects.get(id=1)
        candidate.links.create(url="http://twitter.com/candidato1")
        template_str = get_template('elections/twitter/no_candidator_answer.html')
        context = Context({
            "candidate": candidate,
            "twitter": "candidato1"
            })
        expected_twitter_button = template_str.render(context)
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% no_ha_respondido_twitter_button %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": candidate}))
        self.assertEquals(actual_twitter_button, expected_twitter_button)

    def test_no_tweet_if_candidate_has_no_twitter(self):
        candidate = Candidate.objects.get(id=1)
        expected_twitter_button = ""
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% no_ha_respondido_twitter_button %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": candidate}))
        actual_twitter_button = actual_twitter_button.strip()
        self.assertEquals(actual_twitter_button, expected_twitter_button)

    def test_follow_the_conversation_in_twitter(self):
        candidate = Candidate.objects.get(id=1)
        candidate.links.create(url="http://twitter.com/candidato1_twitter")
        template_str = get_template('elections/twitter/follow_the_conversation.html')
        context = Context({
            "twitter": "candidato1_twitter",
            "candidate": candidate
            })
        expected_twitter_button = template_str.render(context)
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% follow_on_twitter %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": candidate}))
        self.assertEquals(actual_twitter_button, expected_twitter_button)

    def test_ranking_twitter_button(self):
        candidate = Candidate.objects.get(id=1)
        candidate.links.create(url="http://twitter.com/candidato1_twitter")
        template_str = get_template('elections/twitter/ranking_twitter.html')
        context = Context({
            "twitter": "candidato1_twitter",
            "candidate": candidate,
            'btn_text': 'message button',
            'popup_text': 'message twitter window'
            })
        expected_twitter_button = template_str.render(context)
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% twitter_on_ranking 'message button' 'message twitter window' %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": candidate}))
        self.assertEquals(actual_twitter_button, expected_twitter_button)


class QuestionCategoryTestCase(Version2TestCase):
    def setUp(self):
        super(QuestionCategoryTestCase, self).setUp()

    def test_instanciate_one(self):
        category = QuestionCategory.objects.create(name="Perros", election=self.election)
        self.assertIsInstance(category, Category)
