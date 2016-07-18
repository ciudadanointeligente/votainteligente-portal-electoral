# coding=utf-8
from django.core.urlresolvers import reverse
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData
from popular_proposal.forms import ProposalTemporaryDataUpdateForm
from backend_citizen.forms import UserChangeForm
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_citizen.models import Organization


class BackendCitizenViewsTests(BackendCitizenTestCaseBase):
    def setUp(self):
        super(BackendCitizenViewsTests, self).setUp()

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
            'clasification': 'salud',
            'title': u'Que vuelva Fiera',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al equipo una vez al mes',
            'when': u'1_year',
            'causes': u'La terrible de distancia que nos separa',
            'ideal_situation': u'El Feli y el resto de los cabros de la FCI',
            'terms_and_conditions': True
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

    def test_get_update_my_profile(self):
        url = reverse('backend_citizen:update_my_profile')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login')+"?next="+url)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'backend_citizen/update_my_profile.html')
        self.assertIsInstance(response.context['form'], UserChangeForm)

    def test_post_update_my_profile(self):
        url = reverse('backend_citizen:update_my_profile')
        image = self.get_image()
        data = {'first_name': u'Fiera',
                'last_name': 'Feroz',
                'description': u"La más feroz de todas",
                "image": image
                }
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.post(url, data=data, follow=True)
        self.assertTemplateUsed(response, 'backend_citizen/index.html')
        fiera = User.objects.get(id=self.fiera.id)
        self.assertEquals(fiera.profile.description, data['description'])
        self.assertTrue(fiera.profile.image)


class GroupUserCreateView(TestCase):
    def setUp(self):
        super(GroupUserCreateView, self).setUp()

    def test_posting_to_url(self):
        url = reverse('backend_citizen:create_group')
        original_amount = User.objects.count()
        data = {'username': 'group',
                'name': 'This Is a Great Group',
                'email': 'group@mail.com',
                'password1': 'pass',
                'password2': 'pass',
                }
        response = self.client.post(url, data=data)
        registration_complete_url = reverse('registration_activation_complete')
        self.assertRedirects(response, registration_complete_url)
        new_amount = User.objects.count()
        self.assertEquals(new_amount, original_amount + 1)
        tha_group = User.objects.get(username="group")
        self.assertEquals(tha_group.first_name, data['name'])
        self.assertTrue(tha_group.profile.is_organization)


class OrganizationDetailViewTests(TestCase):
    def setUp(self):
        super(OrganizationDetailViewTests, self).setUp()
        self.organization = Organization.objects.create(name=u'La cossa nostra')

    def test_there_is_a_url(self):
        url = reverse('backend_citizen:organization',
                      kwargs={'slug': self.organization.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_citizen/organization.html')
        self.assertEquals(response.context['organization'], self.organization)