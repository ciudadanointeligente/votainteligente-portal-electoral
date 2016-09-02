# coding=utf-8
from django.core.urlresolvers import reverse
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal
from popular_proposal.forms import RejectionForm
from popolo.models import Area
from elections.models import Election, Candidate
from preguntales.models import Message
from django.core import mail


NON_STAFF_PASSWORD = 'gatito'
STAFF_PASSWORD = 'perrito'


class StaffHomeViewTest(TestCase):
    def setUp(self):
        super(StaffHomeViewTest, self).setUp()
        self.non_staff = User.objects.create_user(username='non_staff',
                                                  email='nonstaff@perrito.com',
                                                  password=NON_STAFF_PASSWORD)
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password(STAFF_PASSWORD)
        self.fiera.save()
        self.feli = User.objects.get(username='feli')
        self.arica = Area.objects.get(id='arica-15101')
        self.data = {
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'
        }
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

    def is_reachable_only_by_staff(self, url, url_kwargs=None):
        url = reverse(url, kwargs=url_kwargs)

        # I'm not logged in
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
        return response

    def test_home_view_only_reachable_by_staff_members(self):
        response = self.is_reachable_only_by_staff('backend_staff:index')
        self.assertTemplateUsed(response, 'backend_staff/index.html')

    def test_get_comments_staff_form_for_popular_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        response = self.is_reachable_only_by_staff('backend_staff:popular_proposal_comments',
                                                   url_kwargs={'pk': temporary_data.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['temporary_data'], temporary_data)
        self.assertTemplateUsed(response, 'backend_staff/popular_proposal_comments.html')

    def test_post_comments_on_popular_proposals(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        data = {'problem': u'',
                'when': u'el plazo no está tan weno',
                'solution': u'',
                'allies': u'Los aliados podrían ser mejores'}

        url = reverse('backend_staff:popular_proposal_comments', kwargs={'pk': temporary_data.id})
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_staff/index.html')
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.fiera.first_name, the_mail.body)
        print the_mail.body
        self.fail()

    def test_context(self):
        data = {
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'
        }
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=data)
        temporary_data2 = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                               area=self.arica,
                                                               data=data)
        temporary_data3 = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                               status=ProposalTemporaryData.Statuses.InTheirSide,
                                                               area=self.arica,
                                                               data=data)

        # Temporary datas are listed in the index so we can moderate them
        # or update them.
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='Perrito',
                                         content='content',
                                         )
        # Messages are listed as well

        url = reverse('backend_staff:index')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)

        response = self.client.get(url)

        self.assertIn(temporary_data, response.context['proposals'])
        self.assertIn(temporary_data2, response.context['proposals'])
        self.assertIn(temporary_data3, response.context['proposals'])
        self.assertIn(message, response.context['needing_moderation_messages'].all())

    def test_get_proposal_moderation_view(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('backend_staff:moderate_proposal', kwargs={'pk': temporary_data.id})
        # Credentials checking
        self.assertEquals(self.client.post(url).status_code, 302)
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTemplateNotUsed('backend_staff/index.html')

        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        # It does have a get method
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_staff/proposal_moderation.html')
        form = response.context['form']
        self.assertIsInstance(form, RejectionForm)
        self.assertEquals(form.temporary_data, temporary_data)
        self.assertEquals(form.moderator, self.fiera)

    def test_accept_popular_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('backend_staff:accept_proposal', kwargs={'pk': temporary_data.id})
        # Credentials checking
        self.assertEquals(self.client.post(url).status_code, 302)
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTemplateNotUsed('backend_staff/index.html')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        # It does not have a get method
        response = self.client.get(url)
        self.assertEquals(response.status_code, 405)

        response = self.client.post(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('backend_staff/index.html')
        proposal = PopularProposal.objects.get(data=self.data,
                                               proposer=self.feli,
                                               area=self.arica
                                               )
        self.assertTrue(proposal)

    def test_reject_popular_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('backend_staff:reject_proposal', kwargs={'pk': temporary_data.id})
        # Credentials checking
        self.assertEquals(self.client.post(url).status_code, 302)
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTemplateNotUsed('backend_staff/index.html')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        # It does not have a get method
        response = self.client.get(url)
        self.assertEquals(response.status_code, 405)
        data = {'reason': 'es muy mala'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_staff/index.html')
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.Rejected)
        self.assertEquals(temporary_data.rejected_reason, data['reason'])
