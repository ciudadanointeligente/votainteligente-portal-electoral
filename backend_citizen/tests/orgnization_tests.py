# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from backend_citizen.models import Organization, Enrollment
from images.models import Image
from django.contrib.auth.models import User


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
