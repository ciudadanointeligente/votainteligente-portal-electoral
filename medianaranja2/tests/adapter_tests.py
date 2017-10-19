# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Person, ContactDetail
from elections.models import Candidate, Election, QuestionCategory, PersonalData
from candidator.models import Category, Position, TakenPosition
from django.test import override_settings
from elections.models import Topic
from medianaranja2.adapters import Adapter, Calculator, CommitmentsAdapter
from numpy import matrix, ones
from django.contrib.auth.models import User
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     )

class MediaNaranjaAdaptersBase(TestCase):
    def setUp(self):
        self.election = Election.objects.create(
            name='the name')
        TakenPosition.objects.all().delete()
        self.c1 = Candidate.objects.create(name='C1')
        self.election.candidates.add(self.c1)
        self.c2 = Candidate.objects.create(name='C2')
        self.election.candidates.add(self.c2)
        self.c3 = Candidate.objects.create(name='C3')
        self.election.candidates.add(self.c3)

class AdaptersTest(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(AdaptersTest, self).setUp()
        
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
                                                      person=self.c1,
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
                                                       person=self.c1,
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
                                                       person=self.c1,
                                                       position=self.position5)

    def test_preparing_data(self):
        user_positions = [self.position1, self.position4]
        adapter = Adapter(self.election, user_positions)
        self.assertIn(self.topic1, adapter.topics)
        self.assertIsInstance(adapter.topics, list)
        self.assertIn(self.c1, adapter.candidates)
        self.assertIn(self.c2, adapter.candidates)
        self.assertIsInstance(adapter.candidates, list)
        self.assertEquals(adapter.candidates[0], self.c1)
        self.assertEquals(adapter.candidates[1], self.c2)
        self.assertEquals(adapter.candidates[2], self.c3)
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
        candidate_positions = adapter.get_positions_from_candidate(self.c1)
        expected_positions = [0, 1, 0,1]
        self.assertEquals(candidate_positions, expected_positions)

        P = adapter.get_responses_matrix()
        expected_candidates_response_matrix = [[0, 1, 0,1], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEquals(P, expected_candidates_response_matrix)

    def test_get_result(self):
        TakenPosition.objects.create(topic=self.topic2,
                                     person=self.c3,
                                     position=self.position4)
        TakenPosition.objects.create(topic=self.topic1,
                                     person=self.c3,
                                     position=self.position1)
        positions = [self.position1, self.position4]
        adapter = Adapter(self.election, positions)

        calculator = Calculator()
        calculator.set_questions_adapter(adapter)
        result = calculator._get_questions_vector_result().tolist()
        expected_result = [[1], [0], [2]]
        self.assertEquals(result, expected_result)

        candidate_result = calculator.get_questions_result()
        expected = [{'candidate':self.c3, 'value': 2},
                    {'candidate':self.c1, 'value': 1},
                    {'candidate':self.c2, 'value': 0}]
        self.assertEquals(candidate_result, expected)


class CommitmentsAdaptersTest(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(CommitmentsAdaptersTest, self).setUp()
        proposer = User.objects.create_user(username="proposer")
        self.p1 = PopularProposal.objects.create(proposer=proposer,
                                                 title=u'p1',
                                                 data={}
                                                 )
        self.p2 = PopularProposal.objects.create(proposer=proposer,
                                                 title=u'P2',
                                                 data={}
                                                 )
        self.p3 = PopularProposal.objects.create(proposer=proposer,
                                                 title=u'P3',
                                                 data={}
                                                 )
        #       p1,p2,p3
        # c1 = | 1, 0, 1|
        # c2 = | 1, 1, 1|
        # c3 = | 0, 1, 0|
        commitments = {'c1': [self.p1, self.p3],
                       'c2': [self.p1, self.p2, self.p3],
                       'c3': [self.p2]}
        for key in commitments:
            c = getattr(self, key)
            proposals = commitments[key]
            for proposal in proposals:
                Commitment.objects.create(candidate=c, proposal=proposal, commited=True)

    def test_commitments_matrix(self):
        adapter = CommitmentsAdapter(self.election, [self.p1, self.p3])
        expected_commitments_matrix = [[1, 1], [1, 1], [0,0]]
        C = adapter.get_commitments_matrix().tolist()
        self.assertEquals(C, expected_commitments_matrix)

    def test_get_ones(self):
        adapter = CommitmentsAdapter(self.election, [self.p1, self.p3])
        self.assertEquals(len(adapter.ones), 2)

    def test_get_result(self):
        adapter = CommitmentsAdapter(self.election, [self.p1, self.p3])
        calculator = Calculator()
        calculator.set_commitments_adapter(adapter)
        R = calculator.get_commitments_result().tolist()
        self.assertEquals(R, [[2], [2], [0]])