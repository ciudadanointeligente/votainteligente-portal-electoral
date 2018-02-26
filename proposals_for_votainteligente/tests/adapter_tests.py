# coding=utf-8
from django.test import TestCase
from proposals_for_votainteligente.models import CitizenProposal
from elections.models import Area


class PopularProposalsAdapter(TestCase):
    def setUp(self):
         super(PopularProposalsAdapter, self).setUp()

    def test_login_using_email(self):
        a_comuna = Area.objects.filter(classification='Comuna').first()
        adapter = CitizenProposal(area=a_comuna, generated_at=a_comuna)
        self.assertTrue(adapter)