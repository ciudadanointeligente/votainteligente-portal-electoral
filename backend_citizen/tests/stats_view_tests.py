# coding=utf-8
from django.core.urlresolvers import reverse
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import (ProposalTemporaryData,
                                     ProposalLike,
                                     PopularProposal)
from popular_proposal.forms import ProposalTemporaryDataUpdateForm
from backend_citizen.forms import UserChangeForm
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_citizen.models import Organization
from backend_citizen.stats import StatsPerAreaPerUser
from django.core import mail


class BackendCitizenStatsViewsTests(BackendCitizenTestCaseBase):
    def setUp(self):
        super(BackendCitizenStatsViewsTests, self).setUp()
        self.proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       area=self.arica,
                                                       data=self.data,
                                                       title=u'This is a title'
                                                       )
        self.proposal2 = PopularProposal.objects.create(proposer=self.fiera,
                                                        area=self.arica,
                                                        data=self.data,
                                                        title=u'Proposal2',
                                                        for_all_areas=True

                                                        )

    def test_stats_per_area_per_user_mixin(self):
        stats = StatsPerAreaPerUser(self.arica, self.fiera)
        self.assertIn(self.proposal, stats.local_proposals.all())
        self.assertNotIn(self.proposal2, stats.local_proposals.all())
        self.assertNotIn(self.proposal, stats.for_all_areas_proposals.all())
        self.assertIn(self.proposal2, stats.for_all_areas_proposals.all())
        self.assertIn(self.proposal, stats.all_proposals.all())
        self.assertIn(self.proposal2, stats.all_proposals.all())