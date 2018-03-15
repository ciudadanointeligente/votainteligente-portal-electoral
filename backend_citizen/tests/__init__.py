# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from django.contrib.auth.models import User
from elections.models import Area


PASSWORD = 'perrito'


class BackendCitizenTestCaseBase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(BackendCitizenTestCaseBase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password(PASSWORD)
        self.fiera.save()
        self.arica = Area.objects.get(id=3)
