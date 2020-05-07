# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Person, ContactDetail
from elections.models import Candidate, Election, QuestionCategory, PersonalData
from candidator.models import Category, Position, TakenPosition
from django.template.loader import get_template
from django.template import Context, Template
from django.test import override_settings
from elections.models import Topic
import datetime
from django.utils import timezone
from agenda.models import Activity


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
        candidate = Candidate.objects.create(name="Felipe Feroz")
        self.election.candidates.add(candidate)
        self.assertIsInstance(candidate, Person)

    def test_a_candidate_can_belong_to_more_than_one_election(self):
        candidate = Candidate.objects.create(name="Felipe Feroz")
        '''This is for the very specific case of a second round election'''
        second_round = Election.objects.create(name="SecondRound")
        second_round.candidates.add(candidate)
        self.election.candidates.add(candidate)
        self.assertIn(candidate, second_round.candidates.all())
        self.assertIn(candidate, self.election.candidates.all())

    def test_get_twitter(self):
        candidate = Candidate.objects.get(id=1)
        candidate.add_contact_detail(contact_type="TWITTER", label="@candidato1", value="http://twitter.com/candidato1")
        twitter = candidate.twitter
        self.assertIsInstance(twitter, ContactDetail)
        self.assertEquals(twitter.contact_type, "TWITTER")
        self.assertEquals(twitter.label, "@candidato1")
        self.assertEquals(twitter.value, "http://twitter.com/candidato1")

    def test_get_facebook(self):
        candidate = Candidate.objects.get(id=1)
        candidate.add_contact_detail(contact_type="FACEBOOK", label="Facebook", value="http://facebook.com")
        facebook = candidate.facebook()
        self.assertIsInstance(facebook, ContactDetail)
        self.assertEquals(facebook.contact_type, "FACEBOOK")
        self.assertEquals(facebook.label, "Facebook")
        self.assertEquals(facebook.value, "http://facebook.com")

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
        context = {
            "candidate": candidate,
            "twitter": twitter
            }
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
        context = {
            "twitter": twitter,
            "candidate": candidate
            }
        expected_twitter_button = template_str.render(context)
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% follow_on_twitter %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": candidate}))
        self.assertEquals(actual_twitter_button, expected_twitter_button)

    def test_ranking_twitter_button(self):
        candidate = Candidate.objects.get(id=1)
        candidate.add_contact_detail(contact_type="TWITTER", label="@candidato1_twitter", value="http://twitter.com/candidato1_twitter")
        template_str = get_template('elections/twitter/ranking_twitter.html')
        twitter = candidate.contact_details.get(label="@candidato1_twitter")
        context = {
            "twitter": twitter,
            "candidate": candidate,
            'btn_text': 'message button',
            'popup_text': 'message twitter window'
            }
        expected_twitter_button = template_str.render(context)
        actual_twitter_button_template = Template("{% load votainteligente_extras %}{% twitter_on_ranking 'message button' 'message twitter window' %}")
        actual_twitter_button = actual_twitter_button_template.render(Context({"candidate": candidate}))
        self.assertEquals(actual_twitter_button, expected_twitter_button)

    def test_candidate_has_answered(self):
        TakenPosition.objects.all().delete()
        candidate = Candidate.objects.get(id=1)
        category = QuestionCategory.objects.create(name="Perros", election=self.election)
        topic = Topic.objects.create(
            label=u"Should marijuana be legalized?",
            category=category,
            description=u"This is a description of the topic of marijuana")
        position = Position.objects.create(
            topic=topic,
            label=u"Yes",
            description=u"Yes, means that it is considered a good thing for marijuana to be legalized"
        )
        taken_position = TakenPosition.objects.create(topic=topic,
                                                      person=candidate)
        self.assertFalse(candidate.has_answered)
        taken_position.position = position
        taken_position.save()
        self.assertTrue(candidate.has_answered)
        # The admin can force that the candidate hasnt answered
        candidate.force_has_answer = True
        candidate.save()
        self.assertFalse(candidate.has_answered)

    def test_force_has_answer_false(self):
        '''The possibility for the administrator to display that a candidate hasnt answer'''
        candidate = Candidate.objects.create(name="Felipe Feroz")
        self.election.candidates.add(candidate)
        self.assertFalse(candidate.force_has_answer)

    def test_candidate_ordering(self):
        TakenPosition.objects.all().delete()
        c1 = Candidate.objects.get(id=1)
        c2 = Candidate.objects.get(id=2)
        c2.image = 'perrito.jpeg'
        c2.save()
        c3 = Candidate.objects.get(id=3)
        category = QuestionCategory.objects.create(name="Perros", election=self.election)
        topic = Topic.objects.create(
            label=u"Should marijuana be legalized?",
            category=category,
            description=u"This is a description of the topic of marijuana")
        position = Position.objects.create(
            topic=topic,
            label=u"Yes",
            description=u"Yes, means that it is considered a good thing for marijuana to be legalized"
        )
        taken_position = TakenPosition.objects.create(topic=topic,
                                                      position=position,
                                                      person=c3)
        self.assertEquals(Candidate.answered_first.first(), c3)
        self.assertEquals(Candidate.answered_first.all()[1], c2)

    def test_possible_12_naranja_answers(self):

        c = Candidate.objects.get(id=3)
        possible_answers = Topic.objects.filter(category__in=c.election.categories.all())
        self.assertEquals(possible_answers.count(), c.possible_answers().count())

    def test_candidates_can_have_activities_in_their_agenda(self):
        candidate = Candidate.objects.get(id=3)
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        activity = Activity.objects.create(date=tomorrow,
                                           url='https://perrito.cl/actividad_secreta',
                                           description='This is a description',
                                           location='secret location',
                                           content_object=candidate)
        self.assertTrue(candidate.agenda.all())


class CandidateExtraInfoTestCase(Version2TestCase):
    def test_can_have_extra_info(self):
        candidate = Candidate.objects.get(id=1)
        candidate.extra_info['ribbon'] = "perrito"
        candidate.save()
        self.assertEquals(candidate.extra_info['ribbon'], "perrito")

    @override_settings(DEFAULT_CANDIDATE_EXTRA_INFO={'custom_ribbon': 'ribbon text'})
    def test_default_candidate_extra_info(self):
        candidate = Candidate.objects.get(id=1)
        self.assertEquals(candidate.extra_info['custom_ribbon'], 'ribbon text')

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

    def test_bug_258(self):
        candidate = Candidate.objects.get(id=1)
        candidate.extra_info['custom_ribbon'] = 'Perro grande'
        candidate.extra_info['other_thing'] = 'This is something else'
        candidate.save()
        candidate2 = Candidate.objects.get(id=2)
        self.assertEquals(candidate2.extra_info['custom_ribbon'], 'ribbon text')
        self.assertNotIn('other_thing', candidate2.extra_info.keys())


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
