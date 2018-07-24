# coding=utf-8
from django.test import TestCase
from popular_proposal.models import PopularProposal, Commitment
from merepresenta.models import MeRepresentaPopularProposal, MeRepresentaCommitment, Candidate, Coaligacao, Partido
from django.contrib.auth.models import User
from elections.models import Election
from django.core.urlresolvers import reverse


class MeRepresentaPopularProposalTestCase(TestCase):
    def test_instanciate_a_popular_proposal_as_proxy(self):
        proposer = User.objects.create_user(username="proposer")
        p1 = MeRepresentaPopularProposal.objects.create(proposer=proposer,
                                                 title=u'p1',
                                                 clasification='educ',
                                                 data={}
                                                 )
        self.assertIsInstance(p1, PopularProposal)

    def test_instanciate_commitment_as_proxy(self):
        proposer = User.objects.create_user(username="proposer")
        p1 = MeRepresentaPopularProposal.objects.create(proposer=proposer,
                                                 title=u'p1',
                                                 clasification='educ',
                                                 data={}
                                                 )
        candidate = Candidate.objects.create(name="Candidate 1")
        commitment = MeRepresentaCommitment.objects.create(candidate=candidate,
                                                           proposal=p1,
                                                           detail=u'Yo me comprometo',
                                                           commited=True)

        self.assertIsInstance(commitment, Commitment)

class CandidateTestCase(TestCase):
    def test_instanciate(self):
        candidate = Candidate.objects.create(name="Candidate 1",
                                             cpf='1230',
                                             nome_completo=u'Candidato uno',
                                             numero='190000000560',
                                             race="preta",
                                             original_email='perrito@gatito.com',
                                             email_repeated=False)
        self.assertTrue(candidate)
        self.assertFalse(candidate.is_ghost)

class CoaligacaoTestCase(TestCase):
    def test_instanciate(self):
        coaligacao = Coaligacao.objects.create(name=u"Coaligacao a", initials='CA', number='1234', mark=3)
        self.assertTrue(coaligacao)


class PartidoTestCase(TestCase):
    def test_instanciate(self):
        coaligacao = Coaligacao.objects.create(name=u"Coaligacao a", initials='CA', number='1234', mark=3)
        partido = Partido.objects.create(name=u"Partido de los trabalhadores", initials='PT', number='12345', mark=3, coaligacao=coaligacao)
        self.assertTrue(partido)

    def test_candidate_has_partido(self):
        partido = Partido.objects.create(name=u"Partido de los trabalhadores", initials='PT', number='12345', mark=3)
        candidate = Candidate.objects.create(name="Candidate 1",
                                             cpf='1230',
                                             nome_completo=u'Candidato uno',
                                             numero='190000000560',
                                             race="preta",
                                             original_email='perrito@gatito.com',
                                             partido=partido,
                                             email_repeated=False)
        
        
        self.assertEquals(candidate.partido, partido)