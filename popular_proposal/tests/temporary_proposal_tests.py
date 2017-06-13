# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from backend_citizen.models import Organization
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, ConfirmationOfProposalTemporaryData
from popular_proposal.forms import ProposalForm
from django.core.urlresolvers import reverse
from django.core import mail


class TemporaryDataForPromise(ProposingCycleTestCaseBase):
    def setUp(self):
        super(TemporaryDataForPromise, self).setUp()

    def test_instanciate_one(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              join_advocacy_url=u"http://whatsapp.com/mygroup",
                                                              area=self.arica,
                                                              data=self.data)
        self.assertTrue(temporary_data)
        self.assertTrue(temporary_data.join_advocacy_url)
        self.assertFalse(temporary_data.rejected)
        self.assertFalse(temporary_data.rejected_reason)

        self.assertIsNotNone(temporary_data.comments['title'])
        self.assertIsNotNone(temporary_data.comments['problem'])
        self.assertIsNotNone(temporary_data.comments['solution'])
        self.assertIsNotNone(temporary_data.comments['when'])
        self.assertIsNotNone(temporary_data.comments['causes'])
        self.assertIsNotNone(temporary_data.created)
        self.assertIsNotNone(temporary_data.updated)
        self.assertIsNotNone(temporary_data.overall_comments)
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.InOurSide)
        self.assertIn(temporary_data, self.fiera.temporary_proposals.all())
        self.assertEquals(temporary_data.get_title(), self.data['title'])
        self.assertEquals(str(temporary_data.get_title()), self.data['title'])

    def test_send_temporary_data_new_mail(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        temporary_data.notify_new()
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertTrue(the_mail)
        self.assertIn(self.fiera.email, the_mail.to)

    def test_proposing_with_an_organization(self):
        local_org = Organization.objects.create(name="Local Organization")
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              organization=local_org,
                                                              area=self.arica,
                                                              data=self.data)
        self.assertTrue(temporary_data)
        self.assertEquals(temporary_data.organization, local_org)

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
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        original_amount_of_mails = len(mail.outbox)
        temporary_data.reject('es muy mala la cosa')
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertEquals(temporary_data.rejected_reason, 'es muy mala la cosa')
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.Rejected)
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 1)

        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        # context = Context({'area': self.arica,
        #                    'temporary_data': temporary_data,
        #                    'moderator': self.feli
        #                    })
        # template_body = get_template('mails/popular_proposal_rejected_body.html')
        # template_subject = get_template('mails/popular_proposal_rejected_subject.html')
        # template_body.render(context)
        # template_subject.render(context)
        self.assertTrue(the_mail.body)
        self.assertTrue(the_mail.subject)


class ProposingViewTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(ProposingViewTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password('alvarez')
        self.feli.save()

    def test_get_proposing_view(self):
        url = reverse('popular_proposals:propose', kwargs={'slug': self.arica.id})
        # need to be loggedin
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
        url = reverse('popular_proposals:propose', kwargs={'slug': self.arica.id})

        self.client.login(username=self.feli,
                          password='alvarez')
        self.assertFalse(ProposalTemporaryData.objects.all())
        response = self.client.post(url, data=self.data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('popular_proposal/thanks.html')
        temporary_data = ProposalTemporaryData.objects.get()
        self.assertTrue(temporary_data)


class TemporaryDataConfirmationIdentifier(ProposingCycleTestCaseBase):
    def setUp(self):
        super(TemporaryDataConfirmationIdentifier, self).setUp()
        self.temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                   area=self.arica,
                                                                   data=self.data)

    def test_instanciate(self):
        confirmation = ConfirmationOfProposalTemporaryData.objects.create(temporary_data=self.temporary_data)
        self.assertTrue(confirmation)
        self.assertTrue(confirmation.identifier)
        self.assertFalse(confirmation.confirmed)
        self.assertTrue(confirmation.created)
        self.assertTrue(confirmation.updated)
        self.assertEquals(self.temporary_data.confirmation, confirmation)
        self.assertEquals(len(confirmation.identifier.hex), 32)

    def test_send_confirmation_email(self):
        self.temporary_data.send_confirmation()
        self.assertTrue(self.temporary_data.confirmation)
        self.assertTrue(self.temporary_data.confirmation.identifier)
        self.assertFalse(self.temporary_data.confirmation.confirmed)

        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertTrue(the_mail)
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.temporary_data.confirmation.get_absolute_url(), the_mail.body)
        self.assertIn(self.data['title'], the_mail.body)

    def test_confirm(self):
        self.temporary_data.send_confirmation()
        self.temporary_data.confirmation.confirm()
        self.assertTrue(self.temporary_data.confirmation.confirmed)
        self.assertTrue(self.temporary_data.created_proposal)

    def test_url_get(self):
        self.temporary_data.send_confirmation()
        confirmation = self.temporary_data.confirmation
        url = reverse('popular_proposals:confirm', kwargs={'identifier': confirmation.identifier.hex})
        self.assertEquals(confirmation.get_absolute_url(), url)
        # logging in and confirming
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        confirmation = ConfirmationOfProposalTemporaryData.objects.get(id=confirmation.id)
        self.assertFalse(confirmation.confirmed)
        other_user = User.objects.create_user(username='other_user', password='PASSWORD')
        self.client.login(username=other_user.username, password="PASSWORD")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
        confirmation = ConfirmationOfProposalTemporaryData.objects.get(id=confirmation.id)
        self.assertFalse(confirmation.confirmed)
        self.fiera.set_password('feroz')
        self.fiera.save()
        logged_in = self.client.login(username=self.fiera.username, password='feroz')
        self.assertTrue(logged_in)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        confirmation = ConfirmationOfProposalTemporaryData.objects.get(id=confirmation.id)
        self.assertTrue(confirmation.confirmed)
