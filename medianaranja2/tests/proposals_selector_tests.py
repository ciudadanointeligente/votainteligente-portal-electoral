# coding=utf-8
from .adapter_tests import MediaNaranjaAdaptersBase
from medianaranja2.proposals_getter import (ProposalsGetter,
                                            ProposalsGetterByReadingGroup,
                                            ByOnlySiteProposalGetter)
from elections.models import Area, Election, Candidate
from django.contrib.auth.models import User
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     ProposalLike,
                                     PopularProposalSite,
                                     )
from constance.test import override_config
from django.contrib.sites.models import Site
from medianaranja2.models import ReadingGroup


class ProposalsGetterTestCase(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(ProposalsGetterTestCase, self).setUp()
        self.setUpProposals()

    def test_proposals_get_proposals(self):
        getter = ProposalsGetter()
        proposals = getter.proposals(self.election)
        self.assertIn(self.p1, proposals)
        self.assertIn(self.p2, proposals)
        self.assertIn(self.p3, proposals)

    def test_several_proposals_per_election(self):
        child = Area.objects.create(name="children")
        self.election.area = child
        self.election.save()
        mother = Area.objects.create(name="mother")
        mother.children.add(child)
        child.children.add(mother)
        e1 = Election.objects.create(name='the election_mother',
                                     area=mother,
                                     position='jefe')
        c_1_1 = Candidate.objects.create(name="c_1_1")
        e1.candidates.add(c_1_1)
        c_1_2 = Candidate.objects.create(name="c_1_2")
        e1.candidates.add(c_1_2)
        grand_mother = Area.objects.create(name="grand_mother")
        grand_mother.children.add(mother)

        e2 = Election.objects.create(name='the election_grand_mother',
                                     area=grand_mother,
                                     position='super jefe')
        c_2_1 = Candidate.objects.create(name="c_2_1")
        e2.candidates.add(c_2_1)
        c_2_2 = Candidate.objects.create(name="c_2_2")
        e2.candidates.add(c_2_2)

        proposer = User.objects.create_user(username="dog_proposer")
        pa = PopularProposal.objects.create(proposer=proposer,
                                            title=u'pA',
                                            data={}
                                            )
        pb = PopularProposal.objects.create(proposer=proposer,
                                            title=u'PB',
                                            data={}
                                            )
        pc = PopularProposal.objects.create(proposer=proposer,
                                            title=u'PC',
                                            data={}
                                            )

        Commitment.objects.create(candidate=c_1_1, proposal=pa, commited=True)
        Commitment.objects.create(candidate=c_2_2, proposal=pb, commited=True)
        Commitment.objects.create(candidate=c_2_2, proposal=pb, commited=True)

        getter = ProposalsGetter()
        proposed_proposals = getter.get_all_proposals(child)
        self.assertIn(self.p1, proposed_proposals)
        self.assertIn(self.p2, proposed_proposals)
        self.assertIn(self.p3, proposed_proposals)
        self.assertIn(pa, proposed_proposals)
        self.assertIn(pb, proposed_proposals)
        self.assertNotIn(pc, proposed_proposals)
        self.assertEquals(len(proposed_proposals), 5)

    @override_config(MEDIA_NARANJA_MAX_NUM_PR=2)
    def test_excluding_proposals_by_commitments_and_likes(self):
        child = Area.objects.create(name="children")
        self.election.area = child
        self.election.save()
        liker = User.objects.create_user(username="lovable_user")
        ProposalLike.objects.create(proposal=self.p2, user=liker)
        ProposalLike.objects.create(proposal=self.p3, user=liker)
        getter = ProposalsGetter()
        proposals = getter.get_all_proposals(child)
        self.assertEquals(self.p1, proposals.last())
        self.assertIn(self.p1, proposals)
        self.assertIn(self.p2, proposals)
        self.assertIn(self.p3, proposals)

    def test_get_elections_with_an_election(self):
        getter = ProposalsGetter()
        elections = getter.get_elections(self.election)
        self.assertEquals(elections, [self.election])


class ByLectureGroupAdapterTest(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(ByLectureGroupAdapterTest, self).setUp()
        self.setUpProposals()
        self.child = Area.objects.create(name="children")
        self.election.area = self.child
        self.election.save()
        liker = User.objects.create_user(username="lovable_user")
        liker2 = User.objects.create_user(username="lovable_user2")
        ProposalLike.objects.create(proposal=self.p1, user=liker)
        ProposalLike.objects.create(proposal=self.p3, user=liker)
        ProposalLike.objects.create(proposal=self.p1, user=liker2)


        self.group = ReadingGroup.objects.create(name=u"los del c1")
        self.group.candidates.add(self.c1)

        self.group3 = ReadingGroup.objects.create(name=u"los del c3")
        self.group3.candidates.add(self.c3)

        #       p1,p2,p3
        # c1 = | 1, 0, 1|
        # c2 = | 1, 1, 1|
        # c3 = | 0, 1, 0|

    @override_config(MEDIA_NARANJA_MAX_NUM_PR=2)
    def test_selector(self):
        getter = ProposalsGetterByReadingGroup()
        proposals = getter.get_all_proposals(self.child)
        self.assertIn(self.p1, proposals)
        self.assertIn(self.p2, proposals)
        self.assertNotIn(self.p3, proposals)

    @override_config(MEDIA_NARANJA_MAX_NUM_PR=200)
    def test_selector_when_commitments_are_not_enough(self):

        getter = ProposalsGetterByReadingGroup()
        proposals = getter.get_all_proposals(self.child)
        self.assertIn(self.p1, proposals)
        self.assertIn(self.p2, proposals)
        self.assertIn(self.p3, proposals)

    @override_config(MEDIA_NARANJA_MAX_NUM_PR=200)
    def test_selector_when_commitments_are_not_enough(self):

        getter = ProposalsGetterByReadingGroup()
        proposals = getter.get_all_proposals(self.child)
        self.assertIn(self.p1, proposals)
        self.assertIn(self.p2, proposals)
        self.assertIn(self.p3, proposals)

    @override_config(MEDIA_NARANJA_MAX_NUM_PR=200)
    def test_selector_when_commitments_are_not_enough(self):
        ReadingGroup.objects.all().delete()
        getter = ProposalsGetterByReadingGroup()
        proposals = getter.get_all_proposals(self.child)
        self.assertIn(self.p1, proposals)
        self.assertIn(self.p2, proposals)
        self.assertIn(self.p3, proposals)


class ByOnlySiteProposalGetterTestCase(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(ByOnlySiteProposalGetterTestCase, self).setUp()
        self.setUpProposals()
        liker = User.objects.create_user(username="lovable_user")
        liker2 = User.objects.create_user(username="lovable_user2")
        ProposalLike.objects.create(proposal=self.p1, user=liker)
        ProposalLike.objects.create(proposal=self.p3, user=liker)
        ProposalLike.objects.create(proposal=self.p1, user=liker2)
        self.child = Area.objects.create(name="children")

    @override_config(MEDIA_NARANJA_MAX_NUM_PR=200)
    def test_get_proposals(self):
        site = Site.objects.get_current()
        getter = ByOnlySiteProposalGetter(site=site, proposal_class=PopularProposal)
        # p1 and p3 have site related
        PopularProposalSite.objects.create(popular_proposal=self.p1, site=site)
        PopularProposalSite.objects.create(popular_proposal=self.p3, site=site)
        # p2 does not have anything related
        proposals = getter.get_all_proposals(self.child)
        self.assertIn(self.p1, proposals)
        self.assertIn(self.p3, proposals)
        self.assertNotIn(self.p2, proposals)
