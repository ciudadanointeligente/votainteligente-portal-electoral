# coding=utf-8
from django.core.urlresolvers import reverse
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal
from popular_proposal.forms import ProposalTemporaryDataUpdateForm
from popular_proposal.tests import ProposingCycleTestCaseBase
from popolo.models import Area


PASSWORD = 'perrito'


class BackendCitizenViewsTests(ProposingCycleTestCaseBase):
    def setUp(self):
        super(BackendCitizenViewsTests, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password(PASSWORD)
        self.fiera.save()
        self.arica = Area.objects.get(id='arica-15101')

    def test_my_profile_view(self):
        url = reverse('backend_citizen:index')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login')+"?next="+url)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'backend_citizen/index.html')

    def test_temporary_promise_detail_view(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('backend_citizen:temporary_data_update', kwargs={'pk': temporary_data.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login')+'?next=' + url)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'backend_citizen/temporary_data_update.html')
        self.assertIsInstance(response.context['form'], ProposalTemporaryDataUpdateForm)
        form = response.context['form']
        self.assertEquals(form.temporary_data, temporary_data)

        data = {
            'clasification': 'genero',
            'title': u'Que vuelva Fiera',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al equipo una vez al mes',
            'when': u'1_year',
            'causes': u'La terrible de distancia que nos separa',
            'ideal_situation': u'El Feli y el resto de los cabros de la FCI'
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('backend_citizen/index.html')
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertEquals(temporary_data.data['solution'], data['solution'])

    def test_brings_all_the_proposals_that_are_in_my_side(self):
        t_d1 = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                    area=self.arica,
                                                    status=ProposalTemporaryData.Statuses.InOurSide,
                                                    data=self.data)
        t_d2 = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                    area=self.arica,
                                                    status=ProposalTemporaryData.Statuses.InTheirSide,
                                                    data=self.data)
        t_d3 = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                    area=self.arica,
                                                    status=ProposalTemporaryData.Statuses.Rejected,
                                                    data=self.data)
        t_d4 = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                    area=self.arica,
                                                    status=ProposalTemporaryData.Statuses.Accepted,
                                                    data=self.data)
        url = reverse('backend_citizen:index')
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        temporary_proposals = response.context['temporary_proposals']
        self.assertIn(t_d1, temporary_proposals)
        self.assertIn(t_d2, temporary_proposals)
        self.assertIn(t_d3, temporary_proposals)
        self.assertIn(t_d4, temporary_proposals)
