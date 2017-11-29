# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from votita.models import KidsGathering, KidsProposal
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
import json
import votita.urls
from django.test import override_settings

@override_settings(ROOT_URLCONF='votita.stand_alone_urls')
class VotitaRestAPITestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(VotitaRestAPITestCase, self).setUp()
        self.client = APIClient()

    def test_get_kids_proposal(self):
        kid_proposal = KidsProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'propuesta nna',
                                                          clasification=u'educacion'
                                                      )

        url = reverse('kidsproposal-list')
        response = self.client.get(url, format='json')
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['title'], kid_proposal.title)
        self.assertEquals(content[0]['id'], kid_proposal.id)

    def test_get_kids_gathering(self):
        gathering = KidsGathering.objects.create(proposer=self.fiera,
                                                 name="grupo de amigos",
                                                 school="alguna escuela"
                                                 )
        kid_proposal = KidsProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          gathering=gathering,
                                                          data=self.data,
                                                          title=u'propuesta nna',
                                                          clasification=u'educacion'
                                                      )

        url = reverse('kidsgathering-list')
        response = self.client.get(url, format='json')
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)["results"]
        self.assertEquals(len(content[0]['proposals']), 1)