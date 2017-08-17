# coding=utf-8
from django.test import TestCase
from custom_sites.models import CustomSite
from django.contrib.sites.models import Site

class CustomSitesTestCase(TestCase):
    def setUp(self):
        super(CustomSitesTestCase, self).setUp()

    def test_instanciate(self):
        votita = Site.objects.create(domain="votita.cl", name="votita")
        custom_site = CustomSite.objects.create(site=votita, urlconf='votita.urls')
        self.assertEquals(custom_site.site, votita)
        self.assertEquals(custom_site.urlconf, 'votita.urls')
