# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
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
from elections.models import Candidate
from django.core.urlresolvers import reverse
from elections.models import Area, Election


class CommitmentTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(CommitmentTestCase, self).setUp()
        self.algarrobo = Area.objects.get(id=1)
        self.popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                               area=self.algarrobo,
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
        self.assertTrue(commitment.created)
        self.assertTrue(commitment.updated)
        # testing get_absolute_url
        url = reverse('popular_proposals:commitment', kwargs={'candidate_slug': self.candidate.slug,
                                                              'proposal_slug': self.popular_proposal.slug})
        self.assertEquals(commitment.get_absolute_url(), url)
        self.assertIn(commitment, self.candidate.commitments.all())

    def test_exporter_per_area(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.algarrobo,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.popular_proposal,
                                               detail=u'Yo me comprometo',
                                               commited=True)
        election = Election.objects.get(id=2)
        election.position = u'alcalde'
        election.save()
        exporter = CommitmentsExporter(self.algarrobo)
        self.assertIsInstance(exporter.candidates, list)
        self.assertIn(self.candidate, exporter.candidates)

        self.assertIsInstance(exporter.proposals, list)
        self.assertIn(self.popular_proposal, exporter.proposals)
        candidate2 = Candidate.objects.get(id=2)
        self.assertTrue(exporter.has_commited(self.candidate, self.popular_proposal))
        self.assertFalse(exporter.has_commited(candidate2, self.popular_proposal))
        line = exporter.get_line_for(self.candidate)
        self.assertEquals(line[0], self.candidate.election.position)
        self.assertEquals(line[1], self.candidate.name)
        counter = 1
        for p in exporter.proposals:
            counter += 1
            if exporter.has_commited(self.candidate, p):
                self.assertEquals(line[counter], u'\u2713')
            else:
                self.assertEquals(line[counter], u'')
        header_ = exporter.get_header()
        lines = exporter.get_lines()
        header_size = 3
        header = lines[0:header_size]
        self.assertEquals(header, header_)
        counter = 2
        for p in exporter.proposals:
            self.assertEquals(header[0][counter], 'https://votainteligente.cl' + p.get_absolute_url())
            self.assertEquals(header[2][counter], p.title)
            self.assertEquals(header[1][counter], p.data['clasification'])
            counter += 1

        for i in range(0, len(exporter.candidates)):
            c = exporter.candidates[i]
            line = exporter.get_line_for(c)
            self.assertEquals(lines[i+header_size], line)
        exporter_alcalde = CommitmentsExporter(self.algarrobo, 'alcalde')
        candidate4 = Candidate.objects.get(id=4)
        self.assertNotIn(candidate4, exporter_alcalde.candidates)

    def test_filter_commited(self):
        c1 =Candidate.objects.get(id=1)
        c2 = Candidate.objects.get(id=2)
        c3 = Candidate.objects.get(id=3)
        commitment = Commitment.objects.create(candidate=c1,
                                                       proposal=self.popular_proposal,
                                                       detail=u'Yo me comprometo',
                                                       commited=True)
        commitment2 = Commitment.objects.create(candidate=c2,
                                                       proposal=self.popular_proposal,
                                                       detail=u'Yo me comprometo',
                                                       commited=True)
        commitment3 = Commitment.objects.create(candidate=c3,
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
