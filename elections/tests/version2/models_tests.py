# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Person
from elections.models import Candidate, Election, QuestionCategory
from candidator.models import Category


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


class QuestionCategoryTestCase(Version2TestCase):
    def setUp(self):
        super(QuestionCategoryTestCase, self).setUp()

    def test_instanciate_one(self):
        category = QuestionCategory.objects.create(name="Perros", election=self.election)
        self.assertIsInstance(category, Category)
