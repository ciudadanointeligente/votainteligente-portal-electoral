# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Person, ContactDetail
from elections.models import Candidate, Election, QuestionCategory, Topic, Area
from candidator.models import Category, Position, TakenPosition
from django.template.loader import get_template
from django.template import Context, Template
from django.test import override_settings
from django.contrib.auth.models import User
from popular_proposal.models import PopularProposal, Commitment


class RankingTests(TestCase):
    def setUp(self):
        super(RankingTests, self).setUp()
        TakenPosition.objects.all().delete()
        self.fiera = User.objects.get(username='fiera')
        self.algarrobo = Area.objects.get(id=1)
        self.data = {
            'clasification': 'educacion',
            'title': u'Fiera a Santiago',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos\
 y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'causes': u'La super distancia',
            'terms_and_conditions': True
        }
        self.p1 = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.algarrobo,
                                                 data=self.data,
                                                 title=u'This is a title1',
                                                 clasification=u'education'
                                                 )
        self.p2 = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.algarrobo,
                                                 data=self.data,
                                                 title=u'This is a title2',
                                                 clasification=u'education'
                                                 )
        self.p3 = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.algarrobo,
                                                 data=self.data,
                                                 title=u'This is a title3',
                                                 clasification=u'education'
                                                 )
        self.elections = Election.objects.filter(candidates__id__in=[1, 2, 3, 4, 5, 6]).distinct()
        self.categories = QuestionCategory.objects.filter(election__in=self.elections)
        self.topics = Topic.objects.filter(category__in=self.categories)
        for t in self.topics:
            self.assertTrue(t.positions.all())
        self.candidate1 = Candidate.objects.get(pk=1)
        self.candidate2 = Candidate.objects.get(pk=2)
        self.candidate3 = Candidate.objects.get(pk=3)
        self.candidate4 = Candidate.objects.get(pk=4)
        self.candidate5 = Candidate.objects.get(pk=5)
        self.candidate6 = Candidate.objects.get(pk=6)
        self.topic1 = Topic.objects.get(id=1)
        self.topic2 = Topic.objects.get(id=2)
        self.topic3 = Topic.objects.get(id=3)
        self.topic4 = Topic.objects.get(id=4)
        self.topic5 = Topic.objects.get(id=5)
        self.topic6 = Topic.objects.get(id=6)

    def test_ordering_by_completeness_of_12_naranja(self):
        # candidate 4
        self.assertEquals(self.candidate4.election, self.topic1.election)
        self.assertEquals(self.candidate4.election, self.topic2.election)
        self.assertEquals(self.candidate4.election, self.topic3.election)
        self.assertEquals(Topic.objects.filter(category__in=self.candidate4.election.categories.all()).count(), 3)
        self.candidate4.taken_positions.create(topic=self.topic1, position=self.topic1.positions.first())
        self.candidate4.taken_positions.create(topic=self.topic2, position=self.topic2.positions.first())
        self.candidate4.taken_positions.create(topic=self.topic3, position=self.topic3.positions.first())

        # candidate 3
        self.assertEquals(self.candidate3.election, self.topic4.election)
        self.assertEquals(self.candidate3.election, self.topic5.election)
        self.assertEquals(self.candidate3.election, self.topic6.election)
        self.assertEquals(Topic.objects.filter(category__in=self.candidate3.election.categories.all()).count(), 3)
        self.candidate3.taken_positions.create(topic=self.topic4, position=self.topic4.positions.first())
        self.candidate3.taken_positions.create(topic=self.topic5, position=self.topic5.positions.first())
        # candidate 2
        self.assertEquals(self.candidate2.election, self.topic4.election)
        self.assertEquals(self.candidate2.election, self.topic5.election)
        self.assertEquals(self.candidate2.election, self.topic6.election)
        self.assertEquals(Topic.objects.filter(category__in=self.candidate2.election.categories.all()).count(), 3)
        self.candidate2.taken_positions.create(topic=self.topic4, position=self.topic4.positions.first())

        ordered_candidates = Candidate.ranking.all()
        self.assertEquals(ordered_candidates.count(), Candidate.objects.all().count())
        self.assertEquals(self.candidate4, ordered_candidates[0])
        self.assertEquals(self.candidate3, ordered_candidates[1])
        self.assertEquals(self.candidate2, ordered_candidates[2])
        self.assertEquals(ordered_candidates[0].possible_answers,
                          Topic.objects.filter(category__in=self.candidate4.election.categories.all()).distinct().count())

        self.assertEquals(ordered_candidates[0].num_answers, 3)
        self.assertEquals(ordered_candidates[0].naranja_completeness, float(100))
        self.assertAlmostEqual(ordered_candidates[1].naranja_completeness, (float(2) / float(3)) * 100)
        self.assertAlmostEqual(ordered_candidates[2].naranja_completeness, (float(1) / float(3)) * 100)

    def test_ordering_according_to_commitment(self):
        # Candidate 4 has commited with all proposals
        Commitment.objects.create(candidate=self.candidate4,
                                  proposal=self.p1,
                                  detail=u'Yo me comprometo',
                                  commited=True)
        Commitment.objects.create(candidate=self.candidate4,
                                  proposal=self.p2,
                                  detail=u'Yo no me comprometo',
                                  commited=False)
        Commitment.objects.create(candidate=self.candidate4,
                                  proposal=self.p3,
                                  detail=u'Yo me comprometo',
                                  commited=True)
        # Candidate 3 has commited with 2/3 of the proposals
        Commitment.objects.create(candidate=self.candidate3,
                                  proposal=self.p2,
                                  detail=u'Yo no me comprometo',
                                  commited=False)
        Commitment.objects.create(candidate=self.candidate3,
                                  proposal=self.p3,
                                  detail=u'Yo me comprometo',
                                  commited=True)
        # Candidate 1 has commited with 1/3 of the proposals
        Commitment.objects.create(candidate=self.candidate1,
                                  proposal=self.p2,
                                  detail=u'Yo no me comprometo',
                                  commited=False)
        ordered_candidates = Candidate.ranking.all()
        self.assertEquals(ordered_candidates.count(), Candidate.objects.all().count())
        self.assertEquals(ordered_candidates[1].num_proposals, 3)
        self.assertEquals(ordered_candidates[1].num_commitments, 2)

        self.assertEquals(ordered_candidates[0].commitmenness, float(100))
        self.assertAlmostEqual(ordered_candidates[1].commitmenness, (float(2) / float(3)) * 100)
        self.assertAlmostEqual(ordered_candidates[2].commitmenness, (float(1) / float(3)) * 100)

        self.assertEquals(self.candidate4, ordered_candidates[0])
        self.assertEquals(self.candidate3, ordered_candidates[1])
        self.assertEquals(self.candidate1, ordered_candidates[2])

    def test_get_position_in_ranking(self):
        # Candidate 4 has commited with all proposals
        Commitment.objects.create(candidate=self.candidate4,
                                  proposal=self.p1,
                                  detail=u'Yo me comprometo',
                                  commited=True)
        Commitment.objects.create(candidate=self.candidate4,
                                  proposal=self.p2,
                                  detail=u'Yo no me comprometo',
                                  commited=False)
        Commitment.objects.create(candidate=self.candidate4,
                                  proposal=self.p3,
                                  detail=u'Yo me comprometo',
                                  commited=True)
        # Candidate 3 has commited with 2/3 of the proposals
        Commitment.objects.create(candidate=self.candidate3,
                                  proposal=self.p2,
                                  detail=u'Yo no me comprometo',
                                  commited=False)
        Commitment.objects.create(candidate=self.candidate3,
                                  proposal=self.p3,
                                  detail=u'Yo me comprometo',
                                  commited=True)
        # Candidate 1 has commited with 1/3 of the proposals
        Commitment.objects.create(candidate=self.candidate1,
                                  proposal=self.p2,
                                  detail=u'Yo no me comprometo',
                                  commited=False)

        self.assertEquals(Candidate.ranking.position(self.candidate4), 1)
        self.assertEquals(Candidate.ranking.position(self.candidate3), 2)
        self.assertEquals(Candidate.ranking.position(self.candidate1), 3)
