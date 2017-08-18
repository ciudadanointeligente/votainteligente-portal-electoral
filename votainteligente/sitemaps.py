from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from elections.models import Election, Candidate
from popular_proposal.models import PopularProposal


class ProposalSitemap(Sitemap):
    priority = 0.9
    changefreq = 'never'

    def items(self):
        return PopularProposal.objects.all()


class ElectionsSitemap(Sitemap):
    priority = 0.8
    changefreq = 'never'

    def items(self):
        return Election.objects.filter(searchable=True)


class CandidatesSitemap(Sitemap):
    priority = 0.5
    changefreq = 'never'

    def items(self):
        return Candidate.objects.exclude(elections__isnull=True)

    def location(self, obj):
        return obj.get_absolute_url()
