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
        self.assertEquals(result.data['object_id'], self.c1.id)
        self.assertEquals(result.data['percentage'], 75.0)
        self.assertRedirects(response, result.get_absolute_url())

