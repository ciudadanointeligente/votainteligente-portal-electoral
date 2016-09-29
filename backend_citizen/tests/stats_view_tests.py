# coding=utf-8
from popular_proposal.models import (ProposalTemporaryData,
                                     ProposalLike,
                                     Commitment,
                                     PopularProposal)
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_citizen.stats import StatsPerAreaPerUser, StatsPerProposal, PerUserTotalStats
from elections.models import Election, Candidate
from django.core.urlresolvers import reverse


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
        
        self.candidate1 = Candidate.objects.get(id=1)
        self.election = self.candidate1.election
        self.election.position = 'alcalde'
        self.election.save()
        self.assertEquals(self.candidate1.election, self.election)
        self.candidate2 = Candidate.objects.get(id=2)
        self.assertEquals(self.candidate2.election, self.election)
        self.candidate3 = Candidate.objects.get(id=3)
        self.assertEquals(self.candidate3.election, self.election)
        self.candidate4 = Candidate.objects.get(id=4)
        self.election2 = self.candidate4.election
        self.election2.position = 'concejal'
        self.election2.save()
        self.assertEquals(self.candidate4.election, self.election2)
        self.candidate5 = Candidate.objects.get(id=5)
        self.assertEquals(self.candidate5.election, self.election2)
        self.candidate6 = Candidate.objects.get(id=6)
        self.assertEquals(self.candidate6.election, self.election2)

    def test_per_proposal_stats(self):
        # 2 Alcaldes
        c1 = Commitment.objects.create(candidate=self.candidate1,
                                       proposal=self.proposal,
                                       detail=u'Yo me comprometo',
                                       commited=True)
        c2 = Commitment.objects.create(candidate=self.candidate2,
                                       proposal=self.proposal,
                                       detail=u'Yo me comprometo',
                                       commited=False)
        # 1 concejal
        c3 = Commitment.objects.create(candidate=self.candidate6,
                                       proposal=self.proposal,
                                       detail=u'Yo me comprometo',
                                       commited=True)

        stats = StatsPerProposal(self.proposal)
        self.assertIn(c1, stats.pronouncing().all())
        self.assertIn(c2, stats.pronouncing().all())
        self.assertIn(c3, stats.pronouncing().all())

        self.assertNotIn(c3, stats.pronouncing__alcalde().all())
        self.assertIn(c1, stats.pronouncing__alcalde().all())
        self.assertIn(c2, stats.pronouncing__alcalde().all())

        self.assertNotIn(c1, stats.pronouncing__concejal().all())
        self.assertNotIn(c2, stats.pronouncing__concejal().all())
        self.assertIn(c3, stats.pronouncing__concejal().all())

    def test_stats_in_total(self):
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.alhue,
                                       data=self.data,
                                       title=u'Proposal3'

                                       )
        stats = PerUserTotalStats(self.fiera)
        self.assertEquals(stats.areas_present().count(), 2)
        self.assertIn(self.arica, stats.areas_present().all())
        self.assertIn(self.alhue, stats.areas_present().all())
        c1 = Commitment.objects.create(candidate=self.candidate1,
                                       proposal=self.proposal,
                                       detail=u'Yo me comprometo',
                                       commited=True)
        c2 = Commitment.objects.create(candidate=self.candidate6,
                                       proposal=self.proposal,
                                       detail=u'Yo me comprometo',
                                       commited=True)
        self.assertEquals(stats.areas_with_commitments().count(), 1)
        self.assertIn(self.proposal.area, stats.areas_with_commitments().all())
        self.assertIn(c1, stats.pronouncing__alcalde().all())
        self.assertIn(c2, stats.pronouncing__concejal().all())

    def test_per_proposal_stats_for_citizen(self):
        url = reverse('backend_citizen:stats')
        login_url = reverse('auth_login') + '?next=' + url
        self.assertRedirects(self.client.get(url), login_url)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'backend_citizen/stats.html')
        self.assertIn('stats', response.context)
        expected_proposals = [self.proposal, self.proposal2]
        self.assertEquals(len(response.context['stats']), len(expected_proposals))
        PopularProposal.objects.create(proposer=self.feli,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'ProposalFeli',
                                       for_all_areas=True
                                       )
        for proposal_id in response.context['stats']:
            stats = response.context['stats'][proposal_id]
            self.assertIsInstance(stats, StatsPerProposal)
            self.assertIn(stats.proposal, expected_proposals)

        self.assertIsInstance(response.context['total_stats'], PerUserTotalStats)
        self.assertEquals(response.context['total_stats'].user, self.fiera)

    def test_stats_per_area_per_user_mixin(self):
        stats = StatsPerAreaPerUser(self.arica, self.fiera)
        self.assertIn(self.proposal, stats.local_proposals.all())
        self.assertNotIn(self.proposal2, stats.local_proposals.all())
        self.assertNotIn(self.proposal, stats.for_all_areas_proposals.all())
        self.assertIn(self.proposal2, stats.for_all_areas_proposals.all())
        self.assertIn(self.proposal, stats.all_proposals.all())
        self.assertIn(self.proposal2, stats.all_proposals.all())