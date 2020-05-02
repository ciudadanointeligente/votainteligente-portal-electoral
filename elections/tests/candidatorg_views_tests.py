# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, QuestionCategory, Candidate
from django.core.urlresolvers import reverse
from candidator.models import TakenPosition, Position
from elections.models import Topic
from popolo.models import Person
from candidator.comparer import InformationHolder
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.sites.models import Site
from constance.test import override_config

class CandidateInElectionsViewsTestCase(TestCase):
    def setUp(self):
        super(CandidateInElectionsViewsTestCase, self).setUp()
        self.tarapaca = Election.objects.get(id=1)
        self.coquimbo = Election.objects.get(id=2)

    def test_url_candidate(self):
        url = reverse('candidate_detail_view', kwargs={
            'election_slug': self.tarapaca.slug,
            'slug': self.tarapaca.candidates.all()[0].id
            })
        self.assertTrue(url)

    def test_url_duplicated(self):
        candidate = self.coquimbo.candidates.get(id=1)
        candidate.slug = self.tarapaca.candidates.all()[0].id
        candidate.save()

        url_2 = reverse('candidate_detail_view', kwargs={
            'election_slug': self.coquimbo.slug,
            'slug': candidate.slug
            })

        response = self.client.get(url_2)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.context['election'], self.coquimbo)
        self.assertEqual(response.context['candidate'], candidate)

    @override_config(CANDIDATE_ABSOLUTE_URL_USING_AREA=False)
    def test_candidate_get_absolute_url(self):
        candidate = self.coquimbo.candidates.get(id=1)
        candidate.slug = self.tarapaca.candidates.all()[0].slug
        candidate.save()

        url_2 = reverse('candidate_detail_view', kwargs={
            'election_slug': self.coquimbo.slug,
            'slug': candidate.slug
        })
        self.assertEquals(candidate.get_absolute_url(), url_2)

    @override_config(CANDIDATE_ABSOLUTE_URL_USING_AREA=True)
    def test_candidate_get_absolute_url_with_area(self):
        candidate = self.coquimbo.candidates.get(id=1)
        url = reverse('candidate_detail_view_area', kwargs={
            'area_slug': self.tarapaca.area.slug,
            'slug': candidate.slug
        })
        self.assertEquals(candidate.get_absolute_url(), url)
        url_2 = reverse('candidate_detail_view', kwargs={
            'election_slug': self.coquimbo.slug,
            'slug': candidate.slug
        })

        response = self.client.get(candidate.get_absolute_url())
        self.assertEquals(response.status_code, 200)
        response1 = self.client.get(url_2)
        self.assertEquals(response.content, response1.content)

    def test_url_is_reachable(self):
        url = reverse('candidate_detail_view', kwargs={
            'election_slug': self.tarapaca.slug,
            'slug': self.tarapaca.candidates.all()[0].slug
            })
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('election', response.context)
        self.assertEqual(response.context['election'], self.tarapaca)
        self.assertEqual(response.context['candidate'], self.tarapaca.candidates.all()[0])
        self.assertTemplateUsed(response, 'elections/candidate_detail.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_candidates_ogp(self):
        site = Site.objects.get_current()
        candidate = self.coquimbo.candidates.get(id=1)
        self.assertTrue(candidate.ogp_enabled)
        self.assertIn(candidate.name, candidate.ogp_title())
        self.assertEquals('website', candidate.ogp_type())
        expected_url = "http://%s%s" % (site.domain,
                                        candidate.get_absolute_url())
        self.assertEquals(expected_url, candidate.ogp_url())
        expected_url = "http://%s%s" % (site.domain,
                                        static('img/logo_vi_og.jpg'))
        self.assertEquals(expected_url, candidate.ogp_image())

class QuestionaryInElectionsViewTestCase(TestCase):
    def setUp(self):
        super(QuestionaryInElectionsViewTestCase, self).setUp()
        self.tarapaca = Election.objects.get(id=1)

    def test_url_question(self):
        url = reverse('questionary_detail_view',
            kwargs={'slug': self.tarapaca.slug})
        self.assertTrue(url)

    def test_url_is_reachable(self):
        url = reverse('questionary_detail_view',
            kwargs={'slug': self.tarapaca.slug})
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["election"], self.tarapaca)
        self.assertTemplateUsed(response, 'elections/election_questionary.html')


class FaceToFaceViewTestCase(TestCase):
    def setUp(self):
        super(FaceToFaceViewTestCase, self).setUp()
        self.tarapaca = Election.objects.get(id=1)

    def test_url_face_to_face_two_candidate(self):
        url = reverse('face_to_face_two_candidates_detail_view',
            kwargs={
                'slug': self.tarapaca.slug,
                'slug_candidate_one': self.tarapaca.candidates.all()[0].id,
                'slug_candidate_two': self.tarapaca.candidates.all()[1].id,
            })
        self.assertTrue(url)

    def test_url_face_to_face_one_candidate(self):
        url = reverse('face_to_face_one_candidate_detail_view',
            kwargs={
                'slug': self.tarapaca.slug,
                'slug_candidate_one': self.tarapaca.candidates.all()[0].id
            })
        self.assertTrue(url)

    def test_url_face_to_face_no_candidate(self):
        url = reverse('face_to_face_no_candidate_detail_view',
            kwargs={
                'slug': self.tarapaca.slug
            })
        self.assertTrue(url)

    def test_url_is_reachable_for_two_candidates(self):
        url = reverse('face_to_face_two_candidates_detail_view',
            kwargs={
                'slug': self.tarapaca.slug,
                'slug_candidate_one': self.tarapaca.candidates.all()[0].slug,
                'slug_candidate_two': self.tarapaca.candidates.all()[1].slug,
            })
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/compare_candidates.html')
        self.assertIn('first_candidate', response.context)
        self.assertEqual(response.context['first_candidate'], self.tarapaca.candidates.all()[0])
        self.assertIn('second_candidate', response.context)
        self.assertEqual(response.context['second_candidate'], self.tarapaca.candidates.all()[1])

    def test_url_does_not_throw_errors_if_any_candidate_does_not_exist(self):
        url = reverse('face_to_face_two_candidates_detail_view',
            kwargs={
                'slug': self.tarapaca.slug,
                'slug_candidate_one': self.tarapaca.candidates.all()[0].slug,
                'slug_candidate_two': 'i-do-not-exist',
            })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.context['first_candidate'], self.tarapaca.candidates.all()[0])

        self.assertNotIn('second_candidate', response.context)

    def test_url_is_reachable_for_one_candidates(self):
        url = reverse('face_to_face_one_candidate_detail_view',
            kwargs={
                'slug': self.tarapaca.slug,
                'slug_candidate_one': self.tarapaca.candidates.all()[1].slug,
            })
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/compare_candidates.html')
        self.assertIn('first_candidate', response.context)
        self.assertEqual(response.context['first_candidate'], self.tarapaca.candidates.all()[1])

    def test_url_is_reachable_for_no_one_candidates(self):
        url = reverse('face_to_face_no_candidate_detail_view',
            kwargs={
                'slug': self.tarapaca.slug,
            })
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/compare_candidates.html')

