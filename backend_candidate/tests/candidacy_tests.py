# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Candidate
from popular_proposal.models import Organization, Enrollment
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal
from popular_proposal.forms import ProposalForm
from django.core.urlresolvers import reverse
from django.core import mail
from backend_candidate.models import Candidacy


class CandidacyModelTestCase(TestCase):
    def setUp(self):
        super(CandidacyModelTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.candidate = Candidate.objects.create(name='Candidate')

    def test_instanciate_candidacy(self):
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        self.assertEquals(candidacy.user, self.feli)
        self.assertEquals(candidacy.candidate, self.candidate)
        self.assertTrue(candidacy.created)
        self.assertTrue(candidacy.updated)
