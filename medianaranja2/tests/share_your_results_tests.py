# coding=utf-8
from .adapter_tests import MediaNaranjaAdaptersBase
from medianaranja2.proposals_getter import ProposalsGetter, ProposalsGetterByReadingGroup
from elections.models import Area, Election, Candidate
from django.contrib.auth.models import User
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     ProposalLike,
                                     )
from django.core.urlresolvers import reverse
from medianaranja2.models import SharedResult
from django.contrib.contenttypes.models import ContentType
from medianaranja2.forms import ShareForm
from organization_profiles.models import OrganizationTemplate


class ShareYourResultsTestCase(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(ShareYourResultsTestCase, self).setUp()

    def test_result_sharing_instance(self):
        data = {'object_id': self.c1.id, 'percentage': 75.0}
        content_type = ContentType.objects.get_for_model(Candidate)
        result = SharedResult.objects.create(data=data,
                                             content_type=content_type)
        self.assertTrue(result.identifier)
        self.assertTrue(result.data)
        self.assertTrue(result.get_shared_image())
        self.assertTrue(result.ogp_image())

    def test_get_absolute_url(self):
        data = {'object_id': self.c1.id, 'percentage': 75.0}
        content_type = ContentType.objects.get_for_model(Candidate)
        result = SharedResult.objects.create(data=data, content_type=content_type)
        url = reverse('medianaranja2:share', kwargs={'identifier': result.identifier})

        self.assertEquals(result.get_absolute_url(), url)
        response = self.client.get(url)
        self.assertEquals(response.context['shared_object'], self.c1.id)
        self.assertEquals(response.context['percentage'], 75.0)

    def test_post_and_create_everything(self):
        url = reverse('medianaranja2:create_share')
        content_type = ContentType.objects.get_for_model(Candidate)
        data = {'object_id': self.c1.id, 'percentage': 75.0}
        response = self.client.post(url, data=data)
        result = SharedResult.objects.get()
        self.assertEquals(result.content_type, content_type)
        self.assertEquals(result.data['object_id'], str(self.c1.id))
        self.assertEquals(result.data['percentage'], 75.0)
        self.assertRedirects(response, result.get_absolute_url())

    def test_post_and_create_everything_for_organization_template(self):
        user = User.objects.create(username='ciudadanoi',
                                        first_name='Ciudadano Inteligente',
                                        email='mail@mail.com')
        user.profile.is_organization = True
        user.profile.save()

        org_template = user.organization_template
        url = reverse('medianaranja2:create_share_org')
        content_type = ContentType.objects.get_for_model(OrganizationTemplate)
        data = {'object_id': org_template.id,}
        response = self.client.post(url, data=data)
        result = SharedResult.objects.get()
        self.assertEquals(result.content_type, content_type)

    def test_share_form(self):
        content_type = ContentType.objects.get_for_model(Candidate)
        data = {'object_id': self.c1.id, 'percentage': 75.0}
        form = ShareForm(data, content_type=content_type)
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertEquals(result.content_type, content_type)
        self.assertEquals(result.data['object_id'], str(self.c1.id))
        self.assertEquals(result.data['percentage'], 75.0)

    def test_get_actual_object(self):
        data = {'object_id': self.c1.id, 'percentage': 75.0}
        content_type = ContentType.objects.get_for_model(Candidate)
        result = SharedResult.objects.create(data=data,
                                             content_type=content_type)
        
        self.assertEqual(result.object, self.c1)
