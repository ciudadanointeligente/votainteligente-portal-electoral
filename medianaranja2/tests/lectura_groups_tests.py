# coding=utf-8
from .adapter_tests import MediaNaranjaAdaptersBase
from elections.models import Candidate
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     ProposalLike
                                     )
from medianaranja2.models import ReadingGroup
from django.contrib.auth.models import User
from elections.models import Candidate, Election, Area


class ReadingGroupTestCase(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(ReadingGroupTestCase, self).setUp()
        self.setUpProposals()

    def test_instanciate_and_add_candidates(self):
        group = ReadingGroup.objects.create(name=u"Unión Caótica")
        group.candidates.add(self.c1)
        group.candidates.add(self.c2)
        self.assertIn(self.c1, group.candidates.all())
        self.assertIn(self.c2, group.candidates.all())
        self.assertIn(group, self.c1.groups.all())
        self.assertIn(group, self.c2.groups.all())

    def test_group_get_commitments(self):

        group = ReadingGroup.objects.create(name=u"los del c1")
        group.candidates.add(self.c1)

        self.assertIn(self.p1, group.get_proposals().all())
        self.assertIn(self.p3, group.get_proposals().all())
        self.assertNotIn(self.p2, group.get_proposals().all())

        group2 = ReadingGroup.objects.create(name=u"los del c2")
        group2.candidates.add(self.c2)

        liker = User.objects.create_user(username="lovable_user")
        liker2 = User.objects.create_user(username="lovable_user2")
        ProposalLike.objects.create(proposal=self.p2, user=liker)
        ProposalLike.objects.create(proposal=self.p2, user=liker2)
        ProposalLike.objects.create(proposal=self.p3, user=liker)

        self.assertEquals(self.p2, group2.get_proposals().first())
        self.assertEquals(self.p3, group2.get_proposals().all()[1])
        self.assertEquals(self.p1, group2.get_proposals().last())

    def test_group_get_commitments_only_in_election(self):

        group = ReadingGroup.objects.create(name=u"los del c1")
        group.candidates.add(self.c1)
        a = Area.objects.create(name="Territory2")
        e = Election.objects.create(name="new", area=a)
        c = Candidate.objects.create(name="c")
        e.candidates.add(c)
        group.candidates.add(c)
        Commitment.objects.create(candidate=c, proposal=self.p2, commited=True)

        self.assertNotIn(self.p2, group.get_proposals(elections=[self.election]))