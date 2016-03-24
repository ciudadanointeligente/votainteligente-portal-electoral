# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Area, Organization
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData
from popular_proposal.forms import ProposalForm
from django.core.urlresolvers import reverse
from django.core import mail


class ProposingCycleTestCaseBase(TestCase):
    def setUp(self):
        super(ProposingCycleTestCaseBase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.arica = Area.objects.get(id='arica-15101')
        self.data = {
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'
        }


class TemporaryDataForPromise(ProposingCycleTestCaseBase):
    def setUp(self):
        super(TemporaryDataForPromise, self).setUp()

    def test_instanciate_one(self):
        temporary_area = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        self.assertTrue(temporary_area)
        self.assertFalse(temporary_area.rejected)
        self.assertFalse(temporary_area.rejected_reason)
        self.assertIsNotNone(temporary_area.comments['problem'])
        self.assertIsNotNone(temporary_area.comments['solution'])
        self.assertIsNotNone(temporary_area.comments['when'])
        self.assertIsNotNone(temporary_area.comments['allies'])

    def test_proposing_with_an_organization(self):
        local_org = Organization.objects.create(name="Local Organization")
        temporary_area = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              organization=local_org,
                                                              area=self.arica,
                                                              data=self.data)
        self.assertTrue(temporary_area)
        self.assertEquals(temporary_area.organization, local_org)


class ProposingViewTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(ProposingViewTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password('alvarez')
        self.feli.save()

    def test_get_proposing_view(self):
        url = reverse('popular_proposals:propose', kwargs={'pk': self.arica.id})
        #need to be loggedin
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        form = response.context['form']
        self.assertEquals(self.arica, response.context['area'])
        self.assertIsInstance(form, ProposalForm)

    def test_post_proposing_view(self):
        url = reverse('popular_proposals:propose', kwargs={'pk': self.arica.id})

        self.client.login(username=self.feli,
                          password='alvarez')
        self.assertFalse(ProposalTemporaryData.objects.all())
        response = self.client.post(url, data=self.data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('popular_proposal/thanks.html')
        temporary_data = ProposalTemporaryData.objects.get()
        self.assertTrue(temporary_data)
