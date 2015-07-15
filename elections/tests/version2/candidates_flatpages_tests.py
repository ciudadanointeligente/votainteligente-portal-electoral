# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Candidate, CandidateFlatPage
from django.core.urlresolvers import reverse


class CandidateFlatpagesTestCase(TestCase):
    def setUp(self):
        pass

    def test_instanciate_a_flatpage(self):
        candidate = Candidate.objects.get(id=1)
        candidate.id = 'manuel-rojas'
        candidate.save()
        page = CandidateFlatPage.objects.create(candidate=candidate,
                                                url="problems",
                                                title="Problems",
                                                content="The content"
                                                )
        self.assertIn(page, candidate.flatpages.all())
        self.assertTrue(page)
        self.assertEquals(page.candidate, candidate)
        self.assertTrue(page.get_absolute_url())
        url = reverse('candidate_flatpage', kwargs={'election_slug': candidate.election.slug,
                                                    'slug': candidate.id,
                                                    'url': page.url
                                                    }
                      )
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('flatpage', response.context)
        self.assertEquals(response.context['election'], candidate.election)
        self.assertEquals(response.context['candidate'], candidate)
        self.assertEquals(response.context['flatpage'], page)
        self.assertEquals(url, page.get_absolute_url())
