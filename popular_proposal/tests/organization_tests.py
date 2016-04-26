# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from popular_proposal.models import Organization
from images.models import Image


class OrganizationTestCase(TestCase):
    def setUp(self):
        super(OrganizationTestCase, self).setUp()

    def test_organization_has_images(self):
        organization = Organization.objects.create(name='La Cosa Nostra')
        image = Image.objects.create(content_object=organization)
        self.assertIn(image, organization.images.all())
        self.assertEqual(organization.primary_image(), image.image)
