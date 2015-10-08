# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, Candidate, VotaInteligenteMessage,\
    VotaInteligenteAnswer
from elections.views import RankingMixin
from django.core.urlresolvers import reverse


class RankingTestCaseBase(TestCase):
    def setUp(self):
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        self.candidate4 = Candidate.objects.create(name="Fiera")
        self.candidate4.elections.add(self.election)
        self.message = VotaInteligenteMessage.objects.\
            create(election=self.election,
                   author_name='author',
                   author_email='author@email.com',
                   subject='subject',
                   content='content',
                   slug='subject-slugified',
                   moderated=True
                   )

        self.message.people.add(self.candidate1)
        self.message.people.add(self.candidate2)
        self.message.people.add(self.candidate3)
        self.message.people.add(self.candidate4)
        self.ans11 = VotaInteligenteAnswer.objects.create(content=u'a11',
                                                          message=self.message,
                                                          person=self.candidate1
                                                          )

        self.message2 = VotaInteligenteMessage.objects\
            .create(election=self.election,
                    author_name='author',
                    author_email='author@email.com',
                    subject='subject',
                    content='content',
                    slug='subject-slugified',
                    moderated=True
                    )
        self.message2.people.add(self.candidate1)
        self.message2.people.add(self.candidate2)
        self.message2.people.add(self.candidate3)
        self.message2.people.add(self.candidate4)
        self.ans21 = VotaInteligenteAnswer.objects.create(content=u'a21',
                                                          message=self.message2,
                                                          person=self.candidate1
                                                          )
        self.ans22 = VotaInteligenteAnswer.objects.create(content=u'a22',
                                                          message=self.message2,
                                                          person=self.candidate2
                                                          )

        self.message3 = VotaInteligenteMessage.objects\
            .create(election=self.election,
                    author_name='author',
                    author_email='author@email.com',
                    subject='subject',
                    content='content',
                    slug='subject-slugified'
                    )
        self.message3.people.add(self.candidate1)
        self.message3.people.add(self.candidate2)
        self.message3.people.add(self.candidate3)
        self.message3.people.add(self.candidate4)

        self.ans31 = VotaInteligenteAnswer.objects.create(content=u'a31',
                                                          message=self.message3,
                                                          person=self.candidate1
                                                          )

        self.ans32 = VotaInteligenteAnswer.objects.create(content=u'a32',
                                                          message=self.message3,
                                                          person=self.candidate2
                                                          )

        self.ans34 = VotaInteligenteAnswer.objects.create(content=u'a34',
                                                          message=self.message3,
                                                          person=self.candidate4
                                                          )
        self.message4 = VotaInteligenteMessage.objects\
            .create(election=self.election,
                    author_name='author',
                    author_email='author@email.com',
                    subject='subject',
                    content='content',
                    slug='subject-slugified'
                    )
        self.message4.people.add(self.candidate1)
        self.message4.people.add(self.candidate2)
        self.message4.people.add(self.candidate3)
        # this question wasn't asked to candidate 4
        # self.message4.people.add(self.candidate4)


class RankingTestCase(RankingTestCaseBase):
    def test_mixin(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = self.election.candidates.all()

        ranking = ranking_view.get_ranking()
        self.assertEquals(len(ranking), 4)

    def test_get_all_messages(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = self.election.candidates.all()

        self.assertEquals(ranking_view.all_messages().count(), 4)
        self.assertIn(self.message, ranking_view.all_messages())
        self.assertIn(self.message2, ranking_view.all_messages())
        self.assertIn(self.message3, ranking_view.all_messages())
        self.assertIn(self.message4, ranking_view.all_messages())

    def test_get_all_possible_answers(self):
            ranking_view = RankingMixin()
            ranking_view.candidate_queryset = self.election.candidates.all()
            self.assertEquals(ranking_view.all_possible_answers(), 15)

    def test_get_actual_answered_questions(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = self.election.candidates.all()

        self.assertEquals(ranking_view.actual_answers(), 6)

    def test_get_index(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()
        expected_index = float(15)/float(6)
        self.assertEquals(ranking_view.success_index(), expected_index)

    def test_get_clasified_answered_and_questions_num(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = self.election.candidates.all()

        clasified = ranking_view.get_clasified()

        self.assertEquals(clasified[0]['id'], self.candidate1.id)
        self.assertEquals(clasified[0]['name'], self.candidate1.name)
        self.assertEquals(clasified[0]['candidate'], self.candidate1)
        self.assertEquals(clasified[0]['possible_answers'], 4)

        self.assertEquals(clasified[1]['name'], self.candidate2.name)
        self.assertEquals(clasified[1]['id'], self.candidate2.id)
        self.assertEquals(clasified[1]['candidate'], self.candidate2)
        self.assertEquals(clasified[1]['possible_answers'], 4)

        self.assertEquals(clasified[2]['name'], self.candidate3.name)
        self.assertEquals(clasified[2]['id'], self.candidate3.id)
        self.assertEquals(clasified[2]['candidate'], self.candidate3)
        self.assertEquals(clasified[2]['possible_answers'], 4)

        self.assertEquals(clasified[3]['name'], self.candidate4.name)
        self.assertEquals(clasified[3]['id'], self.candidate4.id)
        self.assertEquals(clasified[3]['candidate'], self.candidate4)
        self.assertEquals(clasified[3]['possible_answers'], 3)

        self.assertEquals(clasified[0]['actual_answers'], 3)
        self.assertEquals(clasified[1]['actual_answers'], 2)
        self.assertEquals(clasified[2]['actual_answers'], 0)
        self.assertEquals(clasified[3]['actual_answers'], 1)

    def test_clasified_points(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = self.election.candidates.all()

        clasified = ranking_view.get_clasified()

        success_index = ranking_view.success_index()

        possible_answers = clasified[0]["possible_answers"]
        actual_answers = clasified[0]["actual_answers"]
        expected_points1 = (success_index*actual_answers -
                            (possible_answers-actual_answers))*possible_answers

        self.assertEquals(clasified[0]['points'], expected_points1)

        possible_answers = clasified[1]["possible_answers"]
        actual_answers = clasified[1]["actual_answers"]
        expected_points1 = (success_index*actual_answers -
                            (possible_answers-actual_answers))*possible_answers

        self.assertEquals(clasified[1]['points'], expected_points1)

        possible_answers = clasified[2]["possible_answers"]
        actual_answers = clasified[2]["actual_answers"]
        expected_points1 = (success_index*actual_answers -
                            (possible_answers-actual_answers))*possible_answers

        self.assertEquals(clasified[2]['points'], expected_points1)

        possible_answers = clasified[3]["possible_answers"]
        actual_answers = clasified[3]["actual_answers"]
        expected_points1 = (success_index*actual_answers -
                            (possible_answers-actual_answers))*possible_answers

        self.assertEquals(clasified[3]['points'], expected_points1)

    def test_get_ordered_clasified(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = self.election.candidates.all()

        ordered = ranking_view.get_ordered()

        self.assertEquals(ordered[0]['candidate'], self.candidate1)
        self.assertEquals(ordered[3]['candidate'], self.candidate3)

    def test_get_good_ones(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = self.election.candidates.all()

        good = ranking_view.get_good()
        self.assertEquals(len(good), 2)
        self.assertEquals(good[0]['candidate'], self.candidate1)
        is_candidate2_or_4 = good[1]['candidate'] == self.candidate2 \
            or good[1]['candidate'] == self.candidate4
        self.assertTrue(is_candidate2_or_4)

    def test_get_bad_ones(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = self.election.candidates.all()

        bad = ranking_view.get_bad()
        self.assertEquals(len(bad), 2)
        self.assertEquals(bad[0]['candidate'], self.candidate3)
        is_candidate2_or_4 = bad[1]['candidate'] == self.candidate2 \
            or bad[1]['candidate'] == self.candidate4
        self.assertTrue(is_candidate2_or_4)

    def test_reach_url_and_has_good_and_bad(self):
        url = reverse('ranking_view', kwargs={'slug': self.election.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['election'], self.election)
        self.assertIn('good', response.context)
        self.assertEquals(len(response.context['good']), 2)
        goods = response.context['good']
        bads = response.context['bad']

        is_candidate2_or_4 = goods[1]['candidate'] == self.candidate2 \
            or goods['candidate'] == self.candidate4

        self.assertEquals(goods[0]['candidate'], self.candidate1)
        self.assertTrue(is_candidate2_or_4)

        self.assertIn('bad', response.context)
        self.assertEquals(len(bads), 2)

        is_candidate2_or_4 = bads[1]['candidate'] == self.candidate2 \
            or bads[1]['candidate'] == self.candidate4

        self.assertEquals(bads[0]['candidate'], self.candidate3)


class QuestionsPerCandidateViewTestCase(RankingTestCaseBase):
    def test_it_is_reachable(self):
        reverse_url = reverse('questions_per_candidate',
                              kwargs={'election_slug': self.election.slug,
                                      'slug': self.candidate1.id})
        response = self.client.get(reverse_url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('candidate', response.context)
        self.assertEquals(response.context['candidate'], self.candidate1)
        self.assertTemplateUsed(response,
                                'elections/questions_per_candidate.html')
        self.assertIn('questions', response.context)
        expected_messages = list(VotaInteligenteMessage.objects.
                                 filter(people=self.candidate1))
        actual_messages = list(response.context['questions'])
        self.assertEquals(actual_messages, expected_messages)
