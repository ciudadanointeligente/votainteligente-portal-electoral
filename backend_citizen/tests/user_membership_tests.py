# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from popolo.models import Organization
from backend_citizen.models import Enrollment


class CitizenMembershipTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(CitizenMembershipTestCase, self).setUp()
        self.org = Organization.objects.create(name="Local Organization")

    def test_relating_a_user_and_an_organization(self):
        membership = Enrollment.objects.create(user=self.feli,
                                               organization=self.org)
        self.assertTrue(membership.created)
        self.assertTrue(membership.updated)
        self.assertIn(membership, self.feli.enrollments.all())
        self.assertIn(membership, self.org.enrollments.all())
