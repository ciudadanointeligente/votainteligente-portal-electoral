# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from backend_citizen.models import Organization, Enrollment
from django.contrib.auth.models import User
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     ProposalLike,
                                     )
from popular_proposal.forms import ProposalForm
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.sites.models import Site
from elections.models import Candidate
from django.core.urlresolvers import reverse


class CommitmentTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(CommitmentTestCase, self).setUp()
        self.popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                               area=self.arica,
                                                               data=self.data,
                                                               title=u'This is a title',
                                                               clasification=u'education'
                                                               )
        self.candidate = Candidate.objects.get(id=1)
        self.like1 = ProposalLike.objects.create(user=self.feli,
                                                 proposal=self.popular_proposal)
        self.like2 = ProposalLike.objects.create(user=self.fiera,
                                                 proposal=self.popular_proposal)


    def test_instanciate_one(self):
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.popular_proposal,
                                               detail=u'Yo me comprometo',
                                               commited=True)

        self.assertTrue(commitment)
        self.assertEquals(commitment.candidate, self.candidate)
        self.assertEquals(commitment.proposal, self.popular_proposal)
        self.assertTrue(commitment.detail)
        # testing get_absolute_url
        url = reverse('popular_proposals:commitment', kwargs={'candidate_slug': self.candidate.id,
                                                              'proposal_slug': self.popular_proposal.slug})
        self.assertEquals(commitment.get_absolute_url(), url)
        self.assertIn(commitment, self.candidate.commitments.all())
