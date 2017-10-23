from .adapter_tests import MediaNaranjaAdaptersBase
from medianaranja2.proposals_getter import ProposalsGetter
from elections.models import Area, Election, Candidate
from django.contrib.auth.models import User
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     )


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