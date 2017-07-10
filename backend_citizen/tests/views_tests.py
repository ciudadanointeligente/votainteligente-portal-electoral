# coding=utf-8
from django.core.urlresolvers import reverse
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import (ProposalTemporaryData,
                                     ProposalLike,
                                     PopularProposal)
from popular_proposal.forms import ProposalTemporaryDataUpdateForm
from popular_proposal.tests import get_example_data_for_testing
from backend_citizen.forms import UserChangeForm
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_citizen.models import Organization
from django.core import mail


class BackendCitizenViewsTests(BackendCitizenTestCaseBase):
    def setUp(self):
        super(BackendCitizenViewsTests, self).setUp()
        self.proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       area=self.arica,
                                                       data=self.data,
                                                       title=u'This is a title'
                                                       )
        self.proposal2 = PopularProposal.objects.create(proposer=self.feli,
                                                        area=self.arica,
                                                        data=self.data,
                                                        title=u'Proposal2'
                                                        )

    def test_my_profile_view(self):
        url = reverse('backend_citizen:index')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login')+"?next="+url)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'backend_citizen/update_my_profile.html')

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

        data = get_example_data_for_testing()
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('backend_citizen/my_proposals.html')
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)

        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.feli.email, the_mail.to)
        self.assertIn(self.feli.email, the_mail.to)
        self.assertIn(str(temporary_data.id), the_mail.body)
        self.assertIn(temporary_data.get_title(), the_mail.body)

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
        url = reverse('backend_citizen:my_proposals')
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
        self.assertRedirects(response, reverse('auth_login') + "?next=" + url)
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
        self.assertTemplateUsed(response, 'backend_citizen/update_my_profile.html')
        fiera = User.objects.get(id=self.fiera.id)
        self.assertEquals(fiera.profile.description, data['description'])
        self.assertTrue(fiera.profile.image)

    def test_list_my_supports(self):
        url = reverse('backend_citizen:my_supports')
        login_url = reverse('auth_login') + '?next=' + url
        self.assertRedirects(self.client.get(url), login_url)

        like = ProposalLike.objects.create(user=self.fiera,
                                           proposal=self.proposal)
        like2 = ProposalLike.objects.create(user=self.fiera,
                                            proposal=self.proposal2)
        like_fiera = ProposalLike.objects.create(user=self.feli,
                                                 proposal=self.proposal)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'backend_citizen/my_supports.html')
        self.assertIn(like, response.context['supports'])
        self.assertIn(like2, response.context['supports'])
        self.assertNotIn(like_fiera, response.context['supports'])


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
        registration_complete_url = reverse('registration_complete')
        self.assertRedirects(response, registration_complete_url)
        new_amount = User.objects.count()
        self.assertEquals(new_amount, original_amount + 1)
        tha_group = User.objects.get(username="group")
        self.assertEquals(tha_group.last_name, data['name'])
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
