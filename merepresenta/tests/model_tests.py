# coding=utf-8
from django.test import TestCase
from popular_proposal.models import PopularProposal, Commitment
from merepresenta.models import MeRepresentaPopularProposal, MeRepresentaCommitment
from django.contrib.auth.models import User
from elections.models import Candidate, Election
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
