from django.contrib.sites.models import Site
from rest_framework.reverse import reverse
from urlparse import urljoin
import re


current_site = Site.objects.get_current()


def get_api_url_for_person(person):
    current_site = Site.objects.get_current()
    api_url = urljoin('http://' + current_site.domain, reverse('person-detail', kwargs={'pk': person.id}))
    if api_url.endswith('/'):
        api_url = api_url[:-1]
    return api_url


def reverse_person_url(url):
    current_site = Site.objects.get_current()
    url_base = urljoin('http://' + current_site.domain, reverse('person-list'))
    url = url.replace(url_base, '')
    if url.endswith('/'):
        url = url[:-1]
    return url