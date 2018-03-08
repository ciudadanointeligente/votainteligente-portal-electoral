from elections.models import Area
from popular_proposal.tests import ProposingCycleTestCaseBase


class VIProposingCycleTestCaseBase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(VIProposingCycleTestCaseBase, self).setUp()
        self.arica = Area.objects.get(id='arica-15101')
        self.alhue = Area.objects.get(id='alhue-13502')
