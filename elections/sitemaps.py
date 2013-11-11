from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from elections.models import Election

class ElectionsSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'never'

    def items(self):
        return Election.objects.filter(searchable=True)
