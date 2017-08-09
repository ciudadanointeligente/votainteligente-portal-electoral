# coding=utf-8
from django.test import TestCase, RequestFactory
from django.contrib.sites.models import Site
from custom_sites.middleware import VotaIcurrentSiteMiddleware
from custom_sites.models import CustomSite


class VotaICurrentSiteMiddlewareTestCase(TestCase):
    def setUp(self):
        super(VotaICurrentSiteMiddlewareTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_get_current_site_if_nothing_is_set(self):
        current_site = Site.objects.get_current()
        middleware = VotaIcurrentSiteMiddleware()
        request = self.factory.get('/')
        middleware.process_request(request)
        self.assertEquals(request.site, current_site)

    def test_retorna_votita_si_la_url_es_votita_punto_ce_ele(self):
        votita = Site.objects.create(domain="votita.cl", name="votita")
        custom_site = CustomSite.objects.create(site=votita, urlconf='votita.urls')
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'votita.cl'
        middleware = VotaIcurrentSiteMiddleware()
        middleware.process_request(request)
        self.assertEquals(request.site, votita)
        self.assertTrue(hasattr(request,'urlconf'))
        self.assertEquals(request.urlconf, custom_site.urlconf)

    def test_retorna_normal_si_la_url_es_votita_punto_ce_ele_pero_no_hay_urlconf(self):
        current_site = Site.objects.get_current()
        votita = Site.objects.create(domain="votita.cl", name="votita")
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'votita.cl'
        middleware = VotaIcurrentSiteMiddleware()
        middleware.process_request(request)
        self.assertEquals(request.site, current_site)
        self.assertFalse(hasattr(request,'urlconf'))
