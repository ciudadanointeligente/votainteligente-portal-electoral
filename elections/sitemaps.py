from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from elections.models import Election
from candideitorg.models import Candidate

class ElectionsSitemap(Sitemap):
    priority = 0.8
    changefreq = 'never'

    def items(self):
        return Election.objects.filter(searchable=True)

class CandidatesSitemap(Sitemap):
	priority = 0.5
	changefreq = 'never'
	
	def items(self):
		return Candidate.objects.all()

	def location(self, obj):
		url = reverse('candidate_detail_view', kwargs={
			'election_slug':obj.election.slug,
			'slug':obj.slug
			})
		return url