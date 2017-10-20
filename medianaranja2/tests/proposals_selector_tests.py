from .adapter_tests import MediaNaranjaAdaptersBase
from medianaranja2.proposals_getter import ProposalsGetter


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