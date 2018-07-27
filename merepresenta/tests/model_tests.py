# coding=utf-8
from django.test import TestCase
from popular_proposal.models import PopularProposal, Commitment
from merepresenta.models import (MeRepresentaPopularProposal,
                                 MeRepresentaCommitment,
                                 Candidate,
                                 Coaligacao,
                                 Partido,
                                 VolunteerInCandidate)
from django.contrib.auth.models import User
from elections.models import Election
from django.utils import timezone
import datetime
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
        self.assertFalse(candidate.facebook_contacted)

class CandidateListForVolunteers(TestCase):
    def test_list_for_volunteers(self):
        ghost = Candidate.objects.create(name="Candidate 1", is_ghost=True)
        facebook = Candidate.objects.create(name="Candidate 2", facebook_contacted=True)
        with_contact = Candidate.objects.create(name="Candidate with Contact")
        with_contact.contacts.create(mail="perrito@gatito.cl")

        candidates = Candidate.for_volunteers.all()
        # Assertions
        self.assertNotIn(ghost, candidates)
        self.assertNotIn(facebook, candidates)
        self.assertNotIn(with_contact, candidates)

    def test_if_has_a_volunteer_looking_for_more_than_an_hour(self):
        volunteer = User.objects.create_user(username='volunteer', is_staff=True)
        always_in_list = Candidate.objects.create(name="Always")
        checked_twenty_nine_minutes_ago = Candidate.objects.create(name="Checked 29 minutes ago")
        checked_thirty_one_minutes_ago = Candidate.objects.create(name="Checked 31 minutes ago")

        minutes = 30

        thirtyone_minutes_ago = timezone.now() - datetime.timedelta(minutes=minutes + 5)
        twentynine_minutes_ago = timezone.now() - datetime.timedelta(minutes=minutes - 1)

        record_31 = VolunteerInCandidate.objects.create(volunteer=volunteer,
                                                        candidate=checked_thirty_one_minutes_ago)
        VolunteerInCandidate.objects.filter(id=record_31.id).update(created=thirtyone_minutes_ago)

        record_29 = VolunteerInCandidate.objects.create(volunteer=volunteer,
                                                        created=twentynine_minutes_ago,
                                                        candidate=checked_twenty_nine_minutes_ago)

        VolunteerInCandidate.objects.filter(id=record_29.id).update(created=twentynine_minutes_ago)
        
        candidates = Candidate.for_volunteers.all()
        self.assertIn(always_in_list, candidates)
        self.assertIn(checked_thirty_one_minutes_ago, candidates)
        self.assertNotIn(checked_twenty_nine_minutes_ago, candidates)



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