# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from popular_proposal.models import PopularProposal, Commitment
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from elections.models import Candidate
import json


class PopularProposalRestAPITestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalRestAPITestCase, self).setUp()
        self.client = APIClient()

    def test_get_proposal(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                      )
        url = reverse('popularproposal-list')
        response = self.client.get(url, format='json')
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['title'], popular_proposal.title)
        self.assertEquals(content[0]['id'], popular_proposal.id)
        self.assertEquals(content[0]['clasification'], popular_proposal.clasification)
        self.assertEquals(content[0]['is_local_meeting'], popular_proposal.is_local_meeting)
        self.assertEquals(content[0]['nro_supports'], popular_proposal.nro_supports)
        self.assertTrue(popular_proposal.created)
        self.assertIn(popular_proposal.get_absolute_url(), content[0]['get_absolute_url'])
        self.assertEquals(self.data, content[0]['data'])
        self.assertEquals(self.fiera.username, content[0]['proposer'])

    def test_get_filtered_proposal(self):
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=u'education'
                                       )
        popular_proposal2 = PopularProposal.objects.create(proposer=self.feli,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                      )
        url = reverse('popularproposal-list') + "?proposer=" + self.feli.username
        response = self.client.get(url, format='json')
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['id'], popular_proposal2.id)

    def test_get_filtered_proposal_2(self):
        p1 = PopularProposal.objects.create(proposer=self.fiera,
                                            area=self.arica,
                                            data=self.data,
                                            title=u'This is a title',
                                            clasification=u'typos'
                                            )
        popular_proposal2 = PopularProposal.objects.create(proposer=self.feli,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                      )
        url = reverse('popularproposal-list') + "?clasification=typos"
        response = self.client.get(url, format='json')
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(len(content), 1)
        self.assertEquals(content[0]['id'], p1.id)

    def test_get_candidates(self):
        url = reverse('candidate-list')
        response = self.client.get(url, format='json')
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(len(content), Candidate.objects.count())
        self.assertTrue(content[0]['name'])
        self.assertTrue(content[0]['id'])


    def test_get_commitments(self):
        any_candidate = Candidate.objects.first()
        popular_proposal2 = PopularProposal.objects.create(proposer=self.feli,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                      )
        commitment = Commitment.objects.create(candidate=any_candidate,
                                               proposal=popular_proposal2,
                                               detail=u'Yo me comprometo',
                                               commited=True)
        url = reverse('commitment-list')
        response = self.client.get(url, format='json')
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(len(content), 1)
        self.assertTrue(content[0]['proposal'])
        self.assertTrue(content[0]['candidate'])
        self.assertEquals(content[0]['detail'], commitment.detail)
        self.assertEquals(content[0]['commited'], commitment.commited)
