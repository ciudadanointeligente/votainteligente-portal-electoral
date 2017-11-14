# coding=utf-8
from django.utils.deprecation import MiddlewareMixin

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from custom_sites.models import CustomSite
from django.core.cache import cache


class VotaIcurrentSiteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            host = request.get_host()
            cache_key = "custom_site_" + host
            site_and_custom = cache.get(cache_key)
            if site_and_custom is None:
                site = Site.objects.get(domain=host)
                custom = CustomSite.objects.get(site=site)
                site_and_custom = (site, custom)
                r = cache.set(cache_key, site_and_custom)
            request.site = site_and_custom[0]
            request.urlconf = site_and_custom[1].urlconf
        except (Site.DoesNotExist, CustomSite.DoesNotExist):
            request.site = get_current_site(request)
