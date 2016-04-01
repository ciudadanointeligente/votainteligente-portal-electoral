# coding=utf-8
from django.core.urlresolvers import reverse
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal


PASSWORD = 'perrito'


class BackendCitizenViewsTests(TestCase):
    def setUp(self):
        super(BackendCitizenViewsTests, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password(PASSWORD)
        self.fiera.save()

    def test_my_profile_view(self):
        url = reverse('backend_citizen:index')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login')+"?next="+url)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'backend_citizen/index.html')
