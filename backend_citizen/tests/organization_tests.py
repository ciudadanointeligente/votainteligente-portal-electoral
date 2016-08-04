# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from backend_citizen.models import Organization, Enrollment
from backend_citizen.forms import OrganizationCreationForm
from images.models import Image
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


PASSWORD = 'perrito'


class OrganizationTestCase(TestCase):
    def setUp(self):
        super(OrganizationTestCase, self).setUp()
        self.org = Organization.objects.create(name="Local Organization")
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password(PASSWORD)
        self.fiera.save()

    def test_organization_get_absolute_url(self):
        url = self.org.get_absolute_url()
        response = self.client.get(url)
        self.assertEquals(response.context['organization'], self.org)

    def test_organization_has_images(self):
        organization = Organization.objects.create(name='La Cosa Nostra')
        image = Image.objects.create(content_object=organization)
        self.assertIn(image, organization.images.all())
        self.assertEqual(organization.primary_image(), image.image)

    def test_relating_a_user_and_an_organization(self):
        membership = Enrollment.objects.create(user=self.feli,
                                               organization=self.org)
        self.assertTrue(membership.created)
        self.assertTrue(membership.updated)
        self.assertIn(membership, self.feli.enrollments.all())
        self.assertIn(membership, self.org.enrollments.all())


class OrganizationCreationAndRelationTestCase(OrganizationTestCase):
    def setUp(self):
        super(OrganizationCreationAndRelationTestCase, self).setUp()

    def test_creation_form(self):
        data = {
            'name': u'Circo Roto',
            'description': u'Una organización de circo callejero'
        }

        form = OrganizationCreationForm(data=data, user=self.fiera)
        self.assertTrue(form.is_valid())
        organization = form.save()
        self.assertEquals(organization.name, data['name'])
        self.assertEquals(organization.description, data['description'])
        self.assertTrue(organization.id)
        self.assertEquals(organization.enrollments.first().organization,
                          organization)

    def test_get_creation_view(self):
        url = reverse('backend_citizen:create_org')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login') + "?next=" + url)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'backend_citizen/create_organization.html')
        self.assertIsInstance(response.context['form'],
                              OrganizationCreationForm)

    def test_post_creation_view(self):
        url = reverse('backend_citizen:create_org')
        data = {
            'name': u'Circo Roto',
            'description': u'Una organización de circo callejero'
        }
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(self.fiera.enrollments.all())
        self.assertTemplateUsed(response, 'backend_citizen/index.html')

    def test_ask_if_user_belongs_to_an_org(self):
        url = reverse('backend_citizen:do_you_belong_to_an_org')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login') + "?next=" + url)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
