# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Person, ContactDetail
from elections.models import Candidate, Election, QuestionCategory, PersonalData
from candidator.models import Category, Position, TakenPosition
from django.test import override_settings
from elections.models import Topic
from medianaranja2.adapters import Adapter, Calculator
from numpy import matrix

class AdaptersTest(TestCase):
    def setUp(self):
        super(AdaptersTest, self).setUp()
        self.election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            extra_info_content=u'Más Información')
        TakenPosition.objects.all().delete()
        self.candidate1 = Candidate.objects.create(name='C1')
        self.election.candidates.add(self.candidate1)
        self.candidate2 = Candidate.objects.create(name='C2')
        self.election.candidates.add(self.candidate2)
        self.category1 = QuestionCategory.objects.create(name="marijuana", election=self.election)
        self.topic1 = Topic.objects.create(
            label=u"Should marijuana be legalized?",
            category=self.category1,
            description=u"This is a description of the topic of marijuana")
        self.position1 = Position.objects.create(
            topic=self.topic1,
            label=u"No"
        )
        self.position2 = Position.objects.create(
            topic=self.topic1,
            label=u"Yes"
        )
        taken_position = TakenPosition.objects.create(topic=self.topic1,
                                                      person=self.candidate1,
                                                      position=self.position2)

        self.category2 = QuestionCategory.objects.create(name="education", election=self.election)
        self.topic2 = Topic.objects.create(
            label=u"Should education be bla bla bla?",
            category=self.category2,
            description=u"This is a description of the topic of marijuana")
        self.position3 = Position.objects.create(
            topic=self.topic2,
            label=u"nones, education nones"
        )
        self.position4 = Position.objects.create(
            topic=self.topic2,
            label=u"Yes, education yes"
        )
        taken_position2 = TakenPosition.objects.create(topic=self.topic2,
                                                       person=self.candidate1,
                                                       position=self.position4)
        self.category3 = QuestionCategory.objects.create(name="health", election=self.election)
        self.topic3 = Topic.objects.create(
            label=u"Should health be bla bla bla?",
            category=self.category3,
            description=u"This is a description of the topic of marijuana")
        self.position5 = Position.objects.create(
            topic=self.topic3,
            label=u"nones, health nones"
        )
        self.position6 = Position.objects.create(
            topic=self.topic3,
            label=u"Yes, health yes"
        )
        taken_position2 = TakenPosition.objects.create(topic=self.topic3,
                                                       person=self.candidate1,
                                                       position=self.position5)

    def test_preparing_data(self):
        user_positions = [self.position1, self.position4]
        adapter = Adapter(self.election, user_positions)
        self.assertIn(self.topic1, adapter.topics)
        self.assertIsInstance(adapter.topics, list)
        self.assertIn(self.candidate1, adapter.candidates)
        self.assertIn(self.candidate2, adapter.candidates)
        self.assertIsInstance(adapter.candidates, list)
        self.assertEquals(adapter.candidates[0], self.candidate1)
        self.assertEquals(adapter.candidates[1], self.candidate2)
        self.assertEquals(adapter.positions[0], self.position1)
        self.assertEquals(adapter.positions[1], self.position2)
        self.assertEquals(adapter.positions[2], self.position3)
        self.assertEquals(adapter.positions[3], self.position4)
        self.assertEquals(adapter.positions[4], self.position5)
        self.assertEquals(adapter.positions[5], self.position6)

    def test_getting_responses_vector(self):
        positions = [self.position1, self.position4]
        adapter = Adapter(self.election, positions)
        R = adapter.get_responses_vector()
        self.assertEquals(R, [1, 0, 0, 1])
        questions = adapter.user_questions
        expected_questions = [self.topic1, self.topic2]
        self.assertEquals(questions, expected_questions)

    def test_get_candidate_positions(self):
        positions = [self.position1, self.position4]
        adapter = Adapter(self.election, positions)
        candidate_positions = adapter.get_positions_from_candidate(self.candidate1)
        expected_positions = [0, 1, 0,1]
        self.assertEquals(candidate_positions, expected_positions)

        P = adapter.get_responses_matrix()
        expected_candidates_response_matrix = [[0, 1, 0,1], [0, 0, 0, 0]]
        self.assertEquals(P, expected_candidates_response_matrix)

    def test_get_result(self):
        candidate3 = Candidate.objects.create(name='C3')
        self.election.candidates.add(candidate3)
        TakenPosition.objects.create(topic=self.topic2,
                                     person=candidate3,
                                     position=self.position4)
        TakenPosition.objects.create(topic=self.topic1,
                                     person=candidate3,
                                     position=self.position1)
        positions = [self.position1, self.position4]
        adapter = Adapter(self.election, positions)

        calculator = Calculator(adapter=adapter)
        result = calculator._get_vector_result().tolist()
        expected_result = [[1], [0], [2]]
        self.assertEquals(result, expected_result)

        candidate_result = calculator.get_result()
        expected = [{'candidate':candidate3, 'value': 2},
                    {'candidate':self.candidate1, 'value': 1},
                    {'candidate':self.candidate2, 'value': 0}]
        self.assertEquals(candidate_result, expected)
