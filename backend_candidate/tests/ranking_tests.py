# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Person, ContactDetail
from elections.models import Candidate, Election, QuestionCategory, PersonalData
from candidator.models import Category, Position, TakenPosition
from django.template.loader import get_template
from django.template import Context, Template
from django.test import override_settings
from elections.models import Topic
from django.contrib.auth.models import User
from backend_candidate.models import Candidacy


class RankingTests(TestCase):
    def setUp(self):
        super(RankingTests, self).setUp()
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

    def test_ordering(self):
        # candidate 4
        self.candidate4.taken_positions.create(topic=self.topic1, position=self.topic1.positions.first())
        self.candidate4.taken_positions.create(topic=self.topic2, position=self.topic2.positions.first())
        self.candidate4.taken_positions.create(topic=self.topic3, position=self.topic3.positions.first())
        self.candidate4.taken_positions.create(topic=self.topic4, position=self.topic4.positions.first())
        self.candidate4.taken_positions.create(topic=self.topic5, position=self.topic5.positions.first())
        self.candidate4.taken_positions.create(topic=self.topic6, position=self.topic6.positions.first())

        # candidate 3
        self.candidate3.taken_positions.create(topic=self.topic1, position=self.topic1.positions.first())
        self.candidate3.taken_positions.create(topic=self.topic2, position=self.topic2.positions.first())
        self.candidate3.taken_positions.create(topic=self.topic3, position=self.topic3.positions.first())
        self.candidate3.taken_positions.create(topic=self.topic4, position=self.topic4.positions.first())
        self.candidate3.taken_positions.create(topic=self.topic5, position=self.topic5.positions.first())

        # candidate 2
        self.candidate2.taken_positions.create(topic=self.topic1, position=self.topic1.positions.first())
        self.candidate2.taken_positions.create(topic=self.topic2, position=self.topic2.positions.first())
        self.candidate2.taken_positions.create(topic=self.topic3, position=self.topic3.positions.first())
        self.candidate2.taken_positions.create(topic=self.topic4, position=self.topic4.positions.first())

        ordered_candidates = Candidate.ranking.all()
        self.assertEquals(self.candidate4, ordered_candidates[0])
        self.assertEquals(self.candidate3, ordered_candidates[1])
        self.assertEquals(self.candidate2, ordered_candidates[2])