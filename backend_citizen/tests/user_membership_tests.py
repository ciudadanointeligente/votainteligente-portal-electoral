# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from popolo.models import Organization
from backend_citizen.models import Enrollment
from backend_citizen.forms import OrganizationForm
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


PASSWORD = 'perrito'


class CitizenMembershipTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(CitizenMembershipTestCase, self).setUp()
        self.org = Organization.objects.create(name="Local Organization")
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password(PASSWORD)
        self.fiera.save()

    def test_relating_a_user_and_an_organization(self):
        membership = Enrollment.objects.create(user=self.feli,
                                               organization=self.org)
        self.assertTrue(membership.created)
        self.assertTrue(membership.updated)
        self.assertIn(membership, self.feli.enrollments.all())
        self.assertIn(membership, self.org.enrollments.all())

    def test_creating_an_organization_form(self):
        data = {'name': 'Circo Roto',
                'facebook_page': 'https://www.facebook.com/circoroto/?fref=ts'
                }
        form = OrganizationForm(data=data,
                                user=self.feli)
        self.assertTrue(form.is_valid())
        organization = form.save()
        self.assertEquals(organization.name, data['name'])
        self.assertIsInstance(organization, Organization)
        self.assertTrue(organization.enrollments.all())
        enrollment = organization.enrollments.first()
        self.assertEquals(enrollment.user, self.feli)

    def test_creating_an_organization_view(self):
        url = reverse('backend_citizen:create_organization')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login')+"?next="+url)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertIsInstance(response.context['form'], OrganizationForm)
        self.assertEquals(response.context['form'].user, self.fiera)
        self.assertTemplateUsed(response, 'backend_citizen/create_organization.html')
        data = {'name': 'Circo Roto',
                'facebook_page': 'https://www.facebook.com/circoroto/?fref=ts'
                }
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertTemplateUsed(response, 'backend_citizen/index.html')
