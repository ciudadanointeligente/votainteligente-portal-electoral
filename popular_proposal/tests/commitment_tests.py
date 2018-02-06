# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from backend_citizen.models import Organization, Enrollment
from django.contrib.auth.models import User
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     ProposalLike,
                                     )
from popular_proposal.forms import ProposalForm
from popular_proposal.exporter import CommitmentsExporter
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from elections.models import Area, Election
from popular_proposal import get_authority_model


authority_model = get_authority_model()


class CommitmentTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(CommitmentTestCase, self).setUp()
        self.algarrobo = Area.objects.get(id='algarrobo-5602')
        self.popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                               area=self.algarrobo,
                                                               data=self.data,
                                                               title=u'This is a title',
                                                               clasification=u'education'
                                                               )
        self.authority = authority_model.objects.get(id=1)
        self.like1 = ProposalLike.objects.create(user=self.feli,
                                                 proposal=self.popular_proposal)
        self.like2 = ProposalLike.objects.create(user=self.fiera,
                                                 proposal=self.popular_proposal)


    def test_instanciate_one(self):
        commitment = Commitment.objects.create(authority=self.authority,
                                               proposal=self.popular_proposal,
                                               detail=u'Yo me comprometo',
                                               commited=True)

        self.assertTrue(commitment)
        self.assertEquals(commitment.authority, self.authority)
        self.assertEquals(commitment.proposal, self.popular_proposal)
        self.assertTrue(commitment.detail)
        self.assertIn(commitment, self.authority.commitments.all())

    def test_get_absolute_url(self):
        commitment = Commitment.objects.create(authority=self.authority,
                                               proposal=self.popular_proposal,
                                               detail=u'Yo me comprometo',
                                               commited=True)
        url = reverse('popular_proposals:commitment', kwargs={'authority_slug': self.authority.id,
                                                              'proposal_slug': self.popular_proposal.slug})
        self.assertEquals(commitment.get_absolute_url(), url)

    def test_filter_commited(self):
        c1 =authority_model.objects.get(id=1)
        c2 = authority_model.objects.get(id=2)
        c3 = authority_model.objects.get(id=3)
        commitment = Commitment.objects.create(authority=c1,
                                                       proposal=self.popular_proposal,
                                                       detail=u'Yo me comprometo',
                                                       commited=True)
        commitment2 = Commitment.objects.create(authority=c2,
                                                       proposal=self.popular_proposal,
                                                       detail=u'Yo me comprometo',
                                                       commited=True)
        commitment3 = Commitment.objects.create(authority=c3,
                                                       proposal=self.popular_proposal,
                                                       detail=u'Yo me comprometo',
                                                       commited=False)
        ## y luego podis hacer algo así:
        self.assertIn(commitment, Commitment.objects.committed())
        self.assertIn(commitment2, Commitment.objects.committed())
        self.assertNotIn(commitment3, Commitment.objects.committed())
        ## Y luego el uncommitted
        self.assertNotIn(commitment, Commitment.objects.uncommitted())
        self.assertNotIn(commitment2, Commitment.objects.uncommitted())
        self.assertIn(commitment3, Commitment.objects.uncommitted())
