# coding=utf-8
from django.test import TestCase
from elections.tests import VotaInteligenteTestCase
from popular_proposal.models import PopularProposal, Commitment
from merepresenta.models import (MeRepresentaPopularProposal,
                                 MeRepresentaCommitment,
                                 Candidate,
                                 Coaligacao,
                                 Partido,
                                 VolunteerInCandidate,
                                 CandidateQuestionCategory,
                                 LGBTQDescription,
                                 RightAnswer,
                                 QuestionCategory)
from django.contrib.auth.models import User
from elections.models import Election, Topic
from candidator.models import Position, TakenPosition
from django.utils import timezone
import datetime
from django.core.urlresolvers import reverse
from merepresenta.voluntarios.models import VolunteerProfile
from backend_candidate.models import Candidacy
from django.test import override_settings
import numpy as np
from merepresenta.match.matrix_builder import (MatrixBuilder,
                                               InformationHolder,
                                               CandidatesRightPositionsVector)
from numpy.testing import assert_equal


class MeRepresentaMatchBase(object):
    def set_data(self):
        self.c1 = Candidate.objects.create(name='c1', cpf='1', gender="F")
        self.c2 = Candidate.objects.create(name='c2', cpf='2', parda=True)
        self.c3 = Candidate.objects.create(name='c3', cpf='3')

        self.cat1 = QuestionCategory.objects.create(name="Pautas LGBT")
        topic = Topic.objects.create(label=u"Adoção de crianças por famílias LGBTs", category=self.cat1)
        yes = Position.objects.create(topic=topic, label=u"Sou a FAVOR da adoção de crianças por famílias LGBTs")
        no = Position.objects.create(topic=topic, label=u"Sou CONTRA a adoção de crianças por famílias LGBTs")
        RightAnswer.objects.create(topic=topic,position=yes)
        TakenPosition.objects.create(topic=topic, person=self.c1, position=yes)
        TakenPosition.objects.create(topic=topic, person=self.c2, position=no)
        TakenPosition.objects.create(topic=topic, person=self.c3, position=yes)
        CandidateQuestionCategory.objects.create(category=self.cat1, candidate=self.c1)

        topic2 = Topic.objects.create(label=u"é A favor?", category=self.cat1)
        yes2 = Position.objects.create(topic=topic2, label=u"Sou a FAVOR")
        no2 = Position.objects.create(topic=topic2, label=u"Sou CONTRA")
        RightAnswer.objects.create(topic=topic2, position=yes2)

        TakenPosition.objects.create(topic=topic2, person=self.c1, position=no2)
        TakenPosition.objects.create(topic=topic2, person=self.c2, position=yes2)
        TakenPosition.objects.create(topic=topic2, person=self.c3, position=yes2)

        self.cat2 = QuestionCategory.objects.create(name="Genero")
        CandidateQuestionCategory.objects.create(category=self.cat2, candidate=self.c2)
        topic3 = Topic.objects.create(label=u"Aborto é A favor?", category=self.cat2)
        yes3 = Position.objects.create(topic=topic3, label=u"Sou a FAVOR")
        no3 = Position.objects.create(topic=topic3, label=u"Sou CONTRA")
        RightAnswer.objects.create(topic=topic3, position=yes3)
        TakenPosition.objects.create(topic=topic3, person=self.c1, position=yes3)
        TakenPosition.objects.create(topic=topic3, person=self.c2, position=no3)
        TakenPosition.objects.create(topic=topic3, person=self.c3, position=no3)

        topic4 = Topic.objects.create(label=u"Monitoramento da Lei do feminicídio", category=self.cat2)
        yes4 = Position.objects.create(topic=topic4, label=u"Sou a FAVOR")
        no4 = Position.objects.create(topic=topic4, label=u"Sou CONTRA")
        RightAnswer.objects.create(topic=topic4, position=yes4)
        TakenPosition.objects.create(topic=topic4, person=self.c1, position=yes4)
        TakenPosition.objects.create(topic=topic4, person=self.c2, position=no4)
        TakenPosition.objects.create(topic=topic4, person=self.c3, position=yes4)

        self.cat3 = QuestionCategory.objects.create(name=u"Corrupção")
        CandidateQuestionCategory.objects.create(category=self.cat3, candidate=self.c3)
        topic5 = Topic.objects.create(label=u"Políticos serem donos de emissoras de rádio e TV", category=self.cat3)
        yes5 = Position.objects.create(topic=topic5, label=u"Sou a FAVOR")
        no5 = Position.objects.create(topic=topic5, label=u"Sou CONTRA")
        RightAnswer.objects.create(topic=topic5, position=no5)
        TakenPosition.objects.create(topic=topic5, person=self.c1, position=yes5)
        TakenPosition.objects.create(topic=topic5, person=self.c2, position=yes5)
        TakenPosition.objects.create(topic=topic5, person=self.c3, position=yes5)
        
@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class QuestionCategoryVectors(TestCase, MeRepresentaMatchBase):
    def setUp(self):
        super(QuestionCategoryVectors, self).setUp()
        self.set_data()

    def test_get_positions_vector_of_categories(self):
        '''
        Aqui o que eu quero lograr é um vector de dimensiones (Nao sei falar portugues)
        Dx1 onde D é a quantidade de possivels respostas, asim:

        yes1 | 1 |
        no1  | 0 |
        yes2 | 1 |
        no2  | 0 |
        yes3 | 0 |
        no3  | 0 |
        yes4 | 0 |
        no4  | 0 |
        yes5 | 0 |
        no5  | 0 |

        Más que só tem os dados do Tema
        '''
        information_holder = InformationHolder(Position.objects.all(), Candidate.objects.all(), QuestionCategory.objects.all())
        right_positions_vector = CandidatesRightPositionsVector(information_holder)
        vector = right_positions_vector.get_positions_vector_for_category(self.cat1)
        self.assertEquals(vector.shape, (Position.objects.count(),))
        expected_vector = np.array([1,0,1,0,0,0,0,0,0,0])

        assert_equal(vector, expected_vector)

    def test_get_matrix_of_positions_and_categories(self):
        information_holder = InformationHolder(Position.objects.all(), Candidate.objects.all(), QuestionCategory.objects.all())
        right_positions_vector = CandidatesRightPositionsVector(information_holder)
        matrix = right_positions_vector.get_matrix_positions_and_categories()
        expected_mat = np.array([[1,0,1,0,0,0,0,0,0,0],
                                 [0,0,0,0,1,0,1,0,0,0],
                                 [0,0,0,0,0,0,0,0,0,1] 
                                 ]).T
        assert_equal(matrix, expected_mat)

    def test_get_zeros_if_not_right_answers_selected(self):
        information_holder = InformationHolder(Position.objects.all(), Candidate.objects.all(), QuestionCategory.objects.all())
        right_positions_vector = CandidatesRightPositionsVector(information_holder)
        vector = right_positions_vector.get_positions_vector_for_category(self.cat1)
        RightAnswer.objects.all().delete()
        expected_vector = np.array([0,0,0,0,0,0,0,0,0,0])

    def test_get_position_vector_respect_with_candidate(self):
        information_holder = InformationHolder(Position.objects.all(), Candidate.objects.all(), QuestionCategory.objects.all())
        right_positions_vector = CandidatesRightPositionsVector(information_holder)
        vector = right_positions_vector.get_positions_vector_for_candidate(self.c1)
        expected_vector = np.array([2,0,0,2,1,0,1,0,1,0])
        assert_equal(vector, expected_vector)

    def test_get_desprivilegios_vector(self):
        information_holder = InformationHolder(Position.objects.all(), Candidate.objects.all(), QuestionCategory.objects.all())
        v = information_holder.get_desprivilegios(Candidate.objects.all())
        self.assertEquals(v.shape, (Candidate.objects.count(), ))
        self.assertTrue(v[0])

    def test_get_matrix_of_candidates_with_positions(self):
        information_holder = InformationHolder(Position.objects.all(), Candidate.objects.all(), QuestionCategory.objects.all())
        right_positions_vector = CandidatesRightPositionsVector(information_holder)
        matrix = right_positions_vector.get_matrix_positions_and_candidates()
        expected_mat = np.array([[2,0,0,2,1,0,1,0,1,0],
                                 [0,1,1,0,0,2,0,2,1,0],
                                 [1,0,1,0,0,1,1,0,2,0]
                                 ])
        assert_equal(matrix, expected_mat)

    def test_get_matrix_of_candidates_and_positions_and_right_positions(self):
        information_holder = InformationHolder(Position.objects.all(), Candidate.objects.all(), QuestionCategory.objects.all())
        right_positions_vector = CandidatesRightPositionsVector(information_holder)
        matrix = right_positions_vector.get_candidates_right_positions_matrix()
        self.assertEquals(matrix.shape, (3 ,3))
        self.assertEquals(matrix[0][0], 2)
        self.assertEquals(matrix[0][1], 2)
        self.assertEquals(matrix[0][2], 0)

    def test_set_electors_categories(self):
        builder = MatrixBuilder()
        builder.set_electors_categories([self.cat1, self.cat2])
        electors_choices = builder.electors_categories
        self.assertEquals(electors_choices.shape, (3,))
        self.assertEquals(electors_choices[0], 3)
        self.assertEquals(electors_choices[1], 3)
        self.assertEquals(electors_choices[2], 1)

    def test_get_candidates_right_answers_vs_electors(self):
        builder = MatrixBuilder()
        builder.set_electors_categories([self.cat1, self.cat2])
        r = builder.get_candidates_result()
        self.assertEquals(r.shape, (Candidate.objects.count(), ))

    def test_get_candidates_full_answer_including_partido(self):
        coaligacao = Coaligacao.objects.create(name=u"Coaligacao a", initials='CA', number='1234')
        Partido.objects.create(name=u"Partido de los trabalhadores",
                               initials='PT',
                               number='12345',
                               mark=3.5,
                               coaligacao=coaligacao)
        peta = Partido.objects.create(name=u"Petronila",
                                      initials='PeTa',
                                      number='1232',
                                      mark=4.5,
                                      coaligacao=coaligacao)
        self.c1.partido = peta
        self.c1.save()
        builder = MatrixBuilder()
        builder.set_electors_categories([self.cat1, self.cat2])
        r = builder.get_result()
        self.assertEquals(r.shape, (Candidate.objects.count(), ))
        self.assertEquals(r[0], 56)
        self.assertEquals(r[1], 4)
        self.assertEquals(r[2], 10)

    def test_get_result_as_dict(self):
        coaligacao = Coaligacao.objects.create(name=u"Coaligacao a", initials='CA', number='1234')
        Partido.objects.create(name=u"Partido de los trabalhadores",
                               initials='PT',
                               number='12345',
                               mark=3.5,
                               coaligacao=coaligacao)
        peta = Partido.objects.create(name=u"Petronila",
                                      initials='PeTa',
                                      number='1232',
                                      mark=4.5,
                                      coaligacao=coaligacao)

        self.c1.partido = peta
        self.c1.save()
        builder = MatrixBuilder()
        builder.set_electors_categories([self.cat1, self.cat2])
        r = builder.get_result_as_array()
        self.assertEquals(r[0]['id'], self.c1.id)
        self.assertEquals(r[0]['nota'], 0.56)
        self.assertEquals(r[1]['id'], self.c2.id)
        self.assertEquals(r[1]['nota'], 0.04)
        self.assertEquals(r[2]['id'], self.c3.id)
        self.assertEquals(r[2]['nota'], 0.10)