# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Area, Organization
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal
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
        self.assertEquals(temporary_area.status, ProposalTemporaryData.Statuses.InOurSide)
        self.assertIn(temporary_area, self.fiera.temporary_proposals.all())

    def test_proposing_with_an_organization(self):
        local_org = Organization.objects.create(name="Local Organization")
        temporary_area = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              organization=local_org,
                                                              area=self.arica,
                                                              data=self.data)
        self.assertTrue(temporary_area)
        self.assertEquals(temporary_area.organization, local_org)

    def test_needing_moderation_proposals(self):
        td_waiting_for_moderation = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                         area=self.arica,
                                                                         data=self.data)
        td_waiting_for_moderation2 = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                          area=self.arica,
                                                                          data=self.data)
        needs_citizen_action = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                    status=ProposalTemporaryData.Statuses.InTheirSide,
                                                                    area=self.arica,
                                                                    data=self.data)
        self.assertIn(td_waiting_for_moderation, ProposalTemporaryData.needing_moderation.all())
        self.assertIn(td_waiting_for_moderation2, ProposalTemporaryData.needing_moderation.all())
        self.assertNotIn(needs_citizen_action, ProposalTemporaryData.needing_moderation.all())

    def test_rejecting_a_proposal(self):
        temporary_area = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        temporary_area.reject('es muy mala la cosa')
        temporary_area = ProposalTemporaryData.objects.get(id=temporary_area.id)
        self.assertEquals(temporary_area.rejected_reason, 'es muy mala la cosa')
        self.assertEquals(temporary_area.status, ProposalTemporaryData.Statuses.Rejected)


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


class PopularProposalTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalTestCase, self).setUp()

    def test_instantiate_one(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          )
        self.assertTrue(popular_proposal.created)
        self.assertTrue(popular_proposal.updated)
        self.assertIn(popular_proposal, self.fiera.proposals.all())
        self.assertIn(popular_proposal, self.arica.proposals.all())

    def test_create_popular_proposal_from_temporary_data(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        popular_proposal = temporary_data.create_proposal()
        self.assertEquals(popular_proposal.proposer, self.fiera)
        self.assertEquals(popular_proposal.area, self.arica)
        self.assertEquals(popular_proposal.data, self.data)
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.Accepted)
