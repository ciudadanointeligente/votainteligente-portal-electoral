# coding=utf-8
from django.core.urlresolvers import reverse
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal
from popular_proposal.forms import RejectionForm
from elections.models import Area
from elections.models import Election, Candidate
from django.core import mail
from backend_staff.forms import AddContactAndSendMailForm
from backend_candidate.models import CandidacyContact


NON_STAFF_PASSWORD = 'gatito'
STAFF_PASSWORD = 'perrito'


class FormsTests(TestCase):
    def setUp(self):
        super(FormsTests, self).setUp()
        self.non_staff = User.objects.create_user(username='non_staff',
                                                  email='nonstaff@perrito.com',
                                                  password=NON_STAFF_PASSWORD)
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password(STAFF_PASSWORD)
        self.fiera.save()
        self.feli = User.objects.get(username='feli')
        self.candidate = Candidate.objects.get(id=1)

    def test_forms_for_adding_contact_and_send_mail(self):
        data = {'mail': 'perrito@mail.com'}
        form = AddContactAndSendMailForm(data=data, candidate=self.candidate)
        self.assertTrue(form.is_valid())
        form.send_mail()
        contact = CandidacyContact.objects.get(mail=data['mail'], candidate=self.candidate)
        self.assertTrue(contact)
        contact = CandidacyContact.objects.get(id=contact.id)
        self.assertEquals(contact.times_email_has_been_sent, 1)
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(contact.initial_password, the_mail.body)

    def test_view_get(self):
        url = reverse('backend_staff:add_contact_and_send_mail', kwargs={'pk': self.candidate.id})

        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # I'm logged in but I'm not staff
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # I'm logged in and I'm staff
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AddContactAndSendMailForm)
        self.assertEquals(response.context['candidate'], self.candidate)

    def test_view_post(self):
        data = {'mail': 'perrito@mail.com'}
        url = reverse('backend_staff:add_contact_and_send_mail', kwargs={'pk': self.candidate.id})
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)
        contact = CandidacyContact.objects.get(mail=data['mail'], candidate=self.candidate)
        self.assertTrue(contact)
        contact = CandidacyContact.objects.get(id=contact.id)
        self.assertEquals(contact.times_email_has_been_sent, 1)
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(contact.initial_password, the_mail.body)


