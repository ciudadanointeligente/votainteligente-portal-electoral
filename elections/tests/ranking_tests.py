# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, VotaInteligenteMessage, VotaInteligenteAnswer
from candideitorg.models import Candidate
from elections.views import RankingMixin

from django.core.urlresolvers import reverse
from popit.models import Person



class RankingBaseTestCase(TestCase):
    def setUp(self):
        super(RankingBaseTestCase, self).setUp()
        self.election = Election.objects.all()[0]
        self.candidate1 = Candidate.objects.get(name="Manuel Rojas").relation.person
        self.candidate2 = Candidate.objects.get(name="Alejandro Guillier").relation.person
        self.candidate3 = Candidate.objects.get(name="Pedro Araya").relation.person
        self.candidate4 = Candidate.objects.get(name="Gisela Contreras").relation.person

        Candidate.objects.exclude(id__in=[self.candidate1.id,
            self.candidate2.id,
            self.candidate3.id,
            self.candidate4.id
            ]).delete()

        Person.objects.exclude(id__in=[self.candidate1.relation.person.id,
            self.candidate2.relation.person.id,
            self.candidate3.relation.person.id,
            self.candidate4.relation.person.id
            ]
            ).delete()
        #Trying to copy it from
        #https://github.com/ciudadanointeligente/votainteligente-primarias/blob/master/elecciones/tests/ranking.py


        self.message1 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message1.people.add(self.candidate1)
        self.message1.people.add(self.candidate2)
        self.message1.people.add(self.candidate3)
        self.message1.people.add(self.candidate4)

        self.answer1_1 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer<number_of_question>_<candidate>',
            message=self.message1,
            person=self.candidate1
            )

        self.message2 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message2'
            , content = u'Qué opina usted sobre el test_accept_message2'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message2.people.add(self.candidate1)
        self.message2.people.add(self.candidate2)
        self.message2.people.add(self.candidate3)
        self.message2.people.add(self.candidate4)
        self.answer2_1 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer2_1',
            message=self.message2,
            person=self.candidate1
            )
        self.answer2_2 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer2_2',
            message=self.message2,
            person=self.candidate2
            )

        
        self.message3 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message3'
            , content = u'Qué opina usted sobre el test_accept_message3'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message3.people.add(self.candidate1)
        self.message3.people.add(self.candidate2)
        self.message3.people.add(self.candidate3)
        self.message3.people.add(self.candidate4)

        self.answer3_1 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer3_1',
            message=self.message3,
            person=self.candidate1
            )
        self.answer3_2 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer3_2',
            message=self.message3,
            person=self.candidate2
            )
        self.answer3_4 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer3_2',
            message=self.message3,
            person=self.candidate4
            )

        self.message4 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message4'
            , content = u'Qué opina usted sobre el test_accept_message4'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message4.people.add(self.candidate1)
        self.message4.people.add(self.candidate2)
        self.message4.people.add(self.candidate3)
        #this question wasn't asked to candidate 4


    def test_mixin(self):

        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        ranking = ranking_view.get_ranking()
        self.assertEquals(len(ranking), 4)


    def test_get_all_messages(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        self.assertEquals(ranking_view.all_messages().count(), 4)
        self.assertIn(self.message1, ranking_view.all_messages())
        self.assertIn(self.message2, ranking_view.all_messages())
        self.assertIn(self.message3, ranking_view.all_messages())
        self.assertIn(self.message4, ranking_view.all_messages())

    def test_get_all_possible_answers(self):

        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        self.assertEquals(ranking_view.all_possible_answers(), 15)

    def test_get_actual_answered_questions(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        self.assertEquals(ranking_view.actual_answers(), 6)

    def test_get_index(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        expected_index = float(15)/float(6)
        self.assertEquals(ranking_view.success_index(), expected_index)


    def test_get_clasified_answered_and_questions_num(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()


        clasified = ranking_view.get_clasified()

        self.assertEquals(clasified[0]['id'], self.candidate1.id)
        self.assertEquals(clasified[0]['name'], self.candidate1.name)
        self.assertEquals(clasified[0]['candidate'], self.candidate1.relation.candidate)
        self.assertEquals(clasified[0]['possible_answers'], 4)
        

        self.assertEquals(clasified[1]['name'], self.candidate2.name)
        self.assertEquals(clasified[1]['id'], self.candidate2.id)
        self.assertEquals(clasified[1]['candidate'], self.candidate2.relation.candidate)
        self.assertEquals(clasified[1]['possible_answers'], 4)
        

        self.assertEquals(clasified[2]['name'], self.candidate3.name)
        self.assertEquals(clasified[2]['id'], self.candidate3.id)
        self.assertEquals(clasified[2]['candidate'], self.candidate3.relation.candidate)
        self.assertEquals(clasified[2]['possible_answers'], 4)
        

        self.assertEquals(clasified[3]['name'], self.candidate4.name)
        self.assertEquals(clasified[3]['id'], self.candidate4.id)
        self.assertEquals(clasified[3]['candidate'], self.candidate4.relation.candidate)
        self.assertEquals(clasified[3]['possible_answers'], 3)


        
        self.assertEquals(clasified[0]['actual_answers'], 3)
        self.assertEquals(clasified[1]['actual_answers'], 2)
        self.assertEquals(clasified[2]['actual_answers'], 0)
        self.assertEquals(clasified[3]['actual_answers'], 1)

    def test_clasified_points(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()


        clasified = ranking_view.get_clasified()

        success_index = ranking_view.success_index()

        possible_answers = clasified[0]["possible_answers"]
        actual_answers = clasified[0]["actual_answers"]
        expected_points1 = (success_index*actual_answers - (possible_answers-actual_answers))*possible_answers

        self.assertEquals(clasified[0]['points'], expected_points1)

        possible_answers = clasified[1]["possible_answers"]
        actual_answers = clasified[1]["actual_answers"]
        expected_points1 = (success_index*actual_answers - (possible_answers-actual_answers))*possible_answers

        self.assertEquals(clasified[1]['points'], expected_points1)
        
        possible_answers = clasified[2]["possible_answers"]
        actual_answers = clasified[2]["actual_answers"]
        expected_points1 = (success_index*actual_answers - (possible_answers-actual_answers))*possible_answers

        self.assertEquals(clasified[2]['points'], expected_points1)

        possible_answers = clasified[3]["possible_answers"]
        actual_answers = clasified[3]["actual_answers"]
        expected_points1 = (success_index*actual_answers - (possible_answers-actual_answers))*possible_answers

        self.assertEquals(clasified[3]['points'], expected_points1)


    def test_get_ordered_clasified(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        ordered = ranking_view.get_ordered()

        self.assertEquals(ordered[0]['candidate'], self.candidate1.relation.candidate)
        self.assertEquals(ordered[3]['candidate'], self.candidate3.relation.candidate)

    def test_get_good_ones(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        good = ranking_view.get_good()
        self.assertEquals(len(good), 2)
        self.assertEquals(good[0]['candidate'], self.candidate1.relation.candidate)
        is_candidate2_or_4 = good[1]['candidate'] == self.candidate2.relation.candidate \
        or good[1]['candidate'] == self.candidate4.relation.candidate
        self.assertTrue(is_candidate2_or_4)



    def test_get_bad_ones(self):
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        bad = ranking_view.get_bad()
        self.assertEquals(len(bad), 2)
        self.assertEquals(bad[0]['candidate'], self.candidate3.relation.candidate)
        is_candidate2_or_4 = bad[1]['candidate'] == self.candidate2.relation.candidate \
        or bad[1]['candidate'] == self.candidate4.relation.candidate
        self.assertTrue(is_candidate2_or_4)

        



    def test_reach_url_and_has_good_and_bad(self):
        url = reverse('ranking_detail_view', kwargs={'slug':self.election.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code,200)
        self.assertEquals(response.context['election'],self.election)
        self.assertIn('good',response.context)
        self.assertEquals(len(response.context['good']), 2)


        is_candidate2_or_4 = response.context['good'][1]['candidate'] == self.candidate2 \
                                or response.context['good']['candidate'] == self.candidate4

        self.assertEquals(response.context['good'][0]['candidate'], self.candidate1)
        self.assertTrue(is_candidate2_or_4)

        self.assertIn('bad', response.context)
        self.assertEquals(len(response.context['bad']), 2)


        is_candidate2_or_4 = response.context['bad'][1]['candidate'] == self.candidate2 \
                                or response.context['bad'][1]['candidate'] == self.candidate4

        self.assertEquals(response.context['bad'][0]['candidate'], self.candidate3)


    def test_if_there_are_no_messages_and_no_answers_then_good_and_bad_are_empty(self):
        #Yuuuhuuu back to writing long test names
        VotaInteligenteMessage.objects.all().delete()
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        good = ranking_view.get_good()
        self.assertEquals(len(good), 0)


        bad = ranking_view.get_bad()
        self.assertEquals(len(bad), 0)

        

    def test_if_there_are_no_answers_then_good_and_bad_are_empty(self):
        VotaInteligenteAnswer.objects.all().delete()
        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        good = ranking_view.get_good()
        self.assertEquals(len(good), 0)


        bad = ranking_view.get_bad()
        self.assertEquals(len(bad), 0)


    def test_it_does_only_include_persons_with_answers_in_the_good_ones(self):
        VotaInteligenteAnswer.objects.exclude(person=self.candidate1).delete()

        ranking_view = RankingMixin()
        ranking_view.candidate_queryset = Candidate.objects.all()

        good = ranking_view.get_good()
        self.assertEquals(len(good), 1)


        bad = ranking_view.get_bad()
        self.assertEquals(len(bad), 3)