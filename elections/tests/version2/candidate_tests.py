# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Person
from elections.models import Candidate, Election


class CandidaTeTestCase(TestCase):
    def setUp(self):
        super(CandidaTeTestCase, self).setUp()
        self.election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            extra_info_content=u'Más Información')

    def test_instanciate(self):
        candidate = Candidate.objects.create(name="Felipe Feroz",
                                             election=self.election
                                             )
        self.assertIsInstance(candidate, Person)
