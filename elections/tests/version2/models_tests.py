# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Person, ContactDetail
from elections.models import Candidate, Election, QuestionCategory, PersonalData
from candidator.models import Category
from django.template.loader import get_template
from django.template import Context, Template
from django.test import override_settings
from elections.models import Topic


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

    def test_get_twitter(self):
        candidate = Candidate.objects.get(id=1)
        candidate.add_contact_detail(contact_type="TWITTER", label="@candidato1", value="http://twitter.com/candidato1")
        twitter = candidate.twitter
        self.assertIsInstance(twitter, ContactDetail)
        self.assertEquals(twitter.contact_type, "TWITTER")
        self.assertEquals(twitter.label, "@candidato1")
        self.assertEquals(twitter.value, "http://twitter.com/candidato1")

    def test_it_creates_a_link_to_the_candidate_twitter(self):
        candidate = Candidate.objects.get(id=1)
        candidate.add_contact_detail(contact_type="TWITTER", label="@candidato1", value="http://twitter.com/candidato1")
        twitter = candidate.contact_details.get(label="@candidato1")
        self.assertEquals(candidate.twitter, twitter)

    def test_it_returns_none_if_there_is_no_twitter_link(self):
        candidate = Candidate.objects.get(id=1)
        self.assertIsNone(candidate.twitter)

    def test_it_only_returns_one_twitter_link(self):
        candidate = Candidate.objects.get(id=1)
        candidate.add_contact_detail(contact_type="TWITTER", label="@candidato1", value="http://twitter.com/candidato1")
        candidate.add_contact_detail(contact_type="TWITTER", label="@candidato1_twitter2", value='http://twitter.com/candidato1_twitter2')

        twitter = candidate.twitter
        self.assertEquals(twitter.contact_type, "TWITTER")
        self.assertEquals(twitter.label, "@candidato1")
        self.assertEquals(twitter.value, "http://twitter.com/candidato1")

    def test_tweet_if_candidator_unanswered(self):
        candidate = Candidate.objects.get(id=1)
        candidate.add_contact_detail(contact_type="TWITTER", label="@candidato1", value="http://twitter.com/candidato1")
        twitter = candidate.contact_details.get(label="@candidato1")
        template_str = get_template('elections/twitter/no_candidator_answer.html')
        context = Context({
            "candidate": candidate,
            "twitter": twitter
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
        candidate.add_contact_detail(contact_type="TWITTER", label="@candidato1_twitter", value="http://twitter.com/candidato1_twitter")
        twitter = candidate.contact_details.get(label="@candidato1_twitter")
        template_str = get_template('elections/twitter/follow_the_conversation.html')
        context = Context({
            "twitter": twitter,
            "candidate": candidate
            })
        expected_twitter_button = template_str.render(context)
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% follow_on_twitter %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": candidate}))
        self.assertEquals(actual_twitter_button, expected_twitter_button)

    def test_ranking_twitter_button(self):
        candidate = Candidate.objects.get(id=1)
        candidate.add_contact_detail(contact_type="TWITTER", label="@candidato1_twitter", value="http://twitter.com/candidato1_twitter")
        template_str = get_template('elections/twitter/ranking_twitter.html')
        twitter = candidate.contact_details.get(label="@candidato1_twitter")
        context = Context({
            "twitter": twitter,
            "candidate": candidate,
            'btn_text': 'message button',
            'popup_text': 'message twitter window'
            })
        expected_twitter_button = template_str.render(context)
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% twitter_on_ranking 'message button' 'message twitter window' %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": candidate}))
        self.assertEquals(actual_twitter_button, expected_twitter_button)


class CandidateExtraInfoTestCase(Version2TestCase):
    def test_can_have_extra_info(self):
        candidate = Candidate.objects.get(id=1)
        candidate.extra_info['ribbon'] = "perrito"
        candidate.save()
        self.assertEquals(candidate.extra_info['ribbon'], "perrito")

    @override_settings(DEFAULT_CANDIDATE_EXTRA_INFO={'ribbon': 'perrito'})
    def test_default_candidate_extra_info(self):
        candidate = Candidate.objects.get(id=1)
        self.assertEquals(candidate.extra_info['ribbon'], 'perrito')

    @override_settings(DEFAULT_CANDIDATE_EXTRA_INFO={'ribbon': 'perrito'})
    def test_do_not_override_settings(self):
        candidate = Candidate.objects.get(id=1)
        candidate.extra_info['ribbon'] = 'Perro grande'
        candidate.save()

        candidate_again = Candidate.objects.get(id=1)
        self.assertEquals(candidate_again.extra_info['ribbon'], 'Perro grande')

    def test_instanciate_a_personal_data(self):
        candidate = Candidate.objects.get(id=1)
        personal_data = PersonalData.objects.create(candidate=candidate, label='Edad', value=u'31 años')
        self.assertEquals(personal_data.label, 'Edad')
        self.assertEquals(personal_data.value, u'31 años')
        self.assertIn(personal_data, candidate.personal_datas.all())


class QuestionCategoryTestCase(Version2TestCase):
    def setUp(self):
        super(QuestionCategoryTestCase, self).setUp()

    def test_instanciate_one(self):
        category = QuestionCategory.objects.create(name="Perros", election=self.election)

        self.assertIsInstance(category, Category)
        self.assertEquals(category.__str__(), u"<Perros> in <the name>")


class TopicTestCase(Version2TestCase):
    def setUp(self):
        super(TopicTestCase, self).setUp()

    def test_election(self):
        category = QuestionCategory.objects.create(name="Perros", election=self.election)
        topic = Topic.objects.create(
            label=u"Should marijuana be legalized?",
            category=category,
            description=u"This is a description of the topic of marijuana")

        self.assertEquals(topic.election, self.election)
