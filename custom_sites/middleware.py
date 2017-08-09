# coding=utf-8
from django.utils.deprecation import MiddlewareMixin

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from custom_sites.models import CustomSite


class VotaIcurrentSiteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            site = Site.objects.get(domain=request.get_host())
            custom = CustomSite.objects.get(site=site)
            request.site = site
            request.urlconf = custom.urlconf
        except (Site.DoesNotExist, CustomSite.DoesNotExist):
            request.site = get_current_site(request)
