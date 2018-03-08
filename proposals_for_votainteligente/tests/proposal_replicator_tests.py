# coding=utf-8
from proposals_for_votainteligente.tests import VIProposingCycleTestCaseBase
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
from elections.models import Area
from proposals_for_votainteligente.replicator import Replicator
from django.core.management import call_command


class ProposalReplicatorTestCase(VIProposingCycleTestCaseBase):
    def setUp(self):
        super(ProposalReplicatorTestCase, self).setUp()
        self.popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                               area=self.arica,
                                                               data=self.data,
                                                               title=u'This needs to be replicated',
                                                               clasification=u'education'
                                                               )
        self.candidate = Candidate.objects.get(id=1)
        self.like1 = ProposalLike.objects.create(user=self.feli,
                                                 proposal=self.popular_proposal)
        self.like2 = ProposalLike.objects.create(user=self.fiera,
                                                 proposal=self.popular_proposal)

    def test_replicate_in_all_areas(self):
        replicator = Replicator(self.popular_proposal)
        replicator.replicate()
        for a in Area.objects.all():
            qs = PopularProposal.objects.filter(area=a,
                                                proposer=self.fiera,
                                                title=self.popular_proposal.title,
                                                clasification=self.popular_proposal.clasification,
                                                data=self.data,
                                                for_all_areas=True
                                                )
            self.assertEquals(len(qs), 1)

        proposal = PopularProposal.objects.get(id=self.popular_proposal.id)
        self.assertTrue(proposal.for_all_areas)

    def test_replicate_excluding_areas(self):
        replicator = Replicator(self.popular_proposal)
        replicator.replicate(exclude=['algarrobo-5602'])
        algarrobo = Area.objects.get(id='algarrobo-5602')
        self.assertFalse(PopularProposal.objects.filter(area=algarrobo, title=self.popular_proposal.title))
        alhue = Area.objects.get(id='alhue-13502')
        qs = PopularProposal.objects.filter(area=alhue,
                                            proposer=self.fiera,
                                            title=self.popular_proposal.title,
                                            clasification=self.popular_proposal.clasification,
                                            data=self.data,
                                            for_all_areas=True
                                            )
        self.assertEquals(len(qs), 1)

    def test_call_command(self):
        call_command('replicate', self.popular_proposal.slug)
        for a in Area.objects.all():
            qs = PopularProposal.objects.filter(area=a,
                                                proposer=self.fiera,
                                                title=self.popular_proposal.title,
                                                clasification=self.popular_proposal.clasification,
                                                data=self.data,
                                                for_all_areas=True
                                                )
            self.assertEquals(len(qs), 1)

    def test_call_command_excluding(self):
        algarrobo = Area.objects.get(id='algarrobo-5602')
        call_command('replicate', self.popular_proposal.slug, algarrobo.id)
        self.assertFalse(PopularProposal.objects.filter(area=algarrobo, title=self.popular_proposal.title))
        alhue = Area.objects.get(id='alhue-13502')
        qs = PopularProposal.objects.filter(area=alhue,
                                            proposer=self.fiera,
                                            title=self.popular_proposal.title,
                                            clasification=self.popular_proposal.clasification,
                                            data=self.data,
                                            for_all_areas=True
                                            )
        self.assertEquals(len(qs), 1)
