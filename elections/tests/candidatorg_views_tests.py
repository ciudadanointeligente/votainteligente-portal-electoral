# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, QuestionCategory, Candidate
from django.core.urlresolvers import reverse
from elections.soul_mate import SoulMateDetailView
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
                'slug_candidate_one': self.tarapaca.candidates.all()[0].id,
                'slug_candidate_two': self.tarapaca.candidates.all()[1].id,
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
                'slug_candidate_one': self.tarapaca.candidates.all()[0].id,
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
                'slug_candidate_one': self.tarapaca.candidates.all()[1].id,
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


class SoulMateTestCase(TestCase):
    def setUp(self):
        super(SoulMateTestCase, self).setUp()
        self.antofa = Election.objects.get(id=2)

    def test_url_better_half(self):
        url = reverse('soul_mate_detail_view',
            kwargs={
                'slug': self.antofa.slug
            })
        self.assertTrue(url)

    def test_url_is_reachable_for_better_half(self):
        url = reverse('soul_mate_detail_view',
            kwargs={
                'slug': self.antofa.slug,
            })
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertIn("election", response.context)
        self.assertEquals(response.context['layout'], "elections/election_base.html")
        self.assertTrue(response.context['result_url'].endswith(url))
        self.assertEquals(response.context["election"], self.antofa)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/soulmate_candidate.html')

    def test_get_embeded_12_naranja(self):
        url = reverse('embedded_soul_mate_detail_view',
            kwargs={
                'slug': self.antofa.slug
            })
        response = self.client.get(url)
        self.assertIn("election", response.context)
        self.assertEquals(response.context["election"], self.antofa)
        self.assertEquals(response.context['layout'], "elections/embedded.html")
        self.assertTrue(response.context['result_url'].endswith(url))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/soulmate_candidate.html')

    def test_view_determine_the_choices(self):
        view = SoulMateDetailView()
        data = {
            "question-0": "8",
            "question-1": "11",
            "question-2": "14",
            "question-id-0": "4",
            "question-id-1": "5",
            "question-id-2": "6"
        }
        taken_positions = view.determine_taken_positions(data)
        self.assertEquals(len(taken_positions), 3)
        self.assertIsInstance(taken_positions[0], TakenPosition)
        self.assertIsInstance(taken_positions[1], TakenPosition)
        self.assertIsInstance(taken_positions[2], TakenPosition)
        fiera_topic = Topic.objects.get(id=4)
        si_fiera = Position.objects.get(id=8)
        self.assertEquals(taken_positions[0].topic, fiera_topic)
        self.assertEquals(taken_positions[0].position, si_fiera)
        with self.assertRaises(Person.DoesNotExist):
            taken_positions[0].person
        benito_topic = Topic.objects.get(id=5)
        si_benito = Position.objects.get(id=11)
        self.assertEquals(taken_positions[1].topic, benito_topic)
        self.assertEquals(taken_positions[1].position, si_benito)
        with self.assertRaises(Person.DoesNotExist):
            taken_positions[1].person
        freedom_topic = Topic.objects.get(id=6)
        no_freedom = Position.objects.get(id=14)
        self.assertEquals(taken_positions[2].topic, freedom_topic)
        self.assertEquals(taken_positions[2].position, no_freedom)
        with self.assertRaises(Person.DoesNotExist):
            taken_positions[2].person

    def test_topic_str(self):
        freedom_topic = Topic.objects.get(id=6)
        self.assertIn(str(freedom_topic.election), str(freedom_topic))
        self.assertIn(freedom_topic.label, str(freedom_topic))

    def test_get_information_holder(self):
        view = SoulMateDetailView()
        view.object = self.antofa
        holder = view.get_information_holder()
        self.assertIsInstance(holder, InformationHolder)
        for candidate in holder.persons:
            self.assertIsInstance(candidate, Candidate)
            self.assertIn(int(candidate.id), [1, 2, 3])

        for category in holder.categories:
            self.assertIsInstance(category, QuestionCategory)
            self.assertIn(int(category.id), [3, 4])

    def test_get_information_holder_with_positions(self):
        view = SoulMateDetailView()
        view.object = self.antofa
        data = {
            "question-0": "8",
            "question-1": "11",
            "question-2": "14",
            "question-id-0": "4",
            "question-id-1": "5",
            "question-id-2": "6"
        }
        holder = view.get_information_holder(data=data)
        for candidate in holder.persons:
            self.assertIsInstance(candidate, Candidate)
            self.assertIn(int(candidate.id), [1, 2, 3])

        for category in holder.categories:
            self.assertIsInstance(category, QuestionCategory)
            self.assertIn(int(category.id), [3, 4])

        for position_id in holder.positions:
            self.assertIsInstance(holder.positions[position_id], TakenPosition)
            self.assertIn(int(holder.positions[position_id].topic.id), [4, 5, 6])
            self.assertIn(int(holder.positions[position_id].position.id), [8, 11, 14])
            with self.assertRaises(Person.DoesNotExist):
                holder.positions[position_id].person

    def test_post_with_data_2(self):
        data = {
            "question-0": "8",
            "question-1": "11",
            "question-2": "13",
            "question-id-0": "4",
            "question-id-1": "5",
            "question-id-2": "6"
        }
        url = reverse('soul_mate_detail_view',
            kwargs={
                'slug': self.antofa.slug,
            })

        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed("elections/soulmate_response.html")
        self.assertIn("election", response.context)
        self.assertEquals(response.context["election"], self.antofa)
        self.assertIn("winner", response.context)
        self.assertIn("candidate", response.context["winner"])
        self.assertIsInstance(response.context["winner"]["candidate"], Candidate)
        self.assertIn("others", response.context)

        candidatos_antofa = self.antofa.candidates.all()
        self.assertIn(response.context["winner"]["candidate"], candidatos_antofa)
        self.assertGreater(response.context["winner"]['percentage'], 0.0)

    def test_post_with_data_tie(self):
        data = {
            "question-0": "0",
            "question-1": "11",
            "question-2": "13",
            "question-id-0": "4",
            "question-id-1": "5",
            "question-id-2": "6"
        }
        url = reverse('soul_mate_detail_view',
            kwargs={
                'slug': self.antofa.slug,
            })

        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed("elections/soulmate_response.html")
        self.assertIn("election", response.context)
        self.assertEquals(response.context["election"], self.antofa)
        self.assertNotIn("winner", response.context)
        self.assertIn("others", response.context)
        candidate1 = Candidate.objects.get(id=1)
        candidate3 = Candidate.objects.get(id=3)
        self.assertEquals(response.context['others'][0]['percentage'],
                          response.context['others'][1]['percentage'])
        self.assertIn(response.context['others'][0]['candidate'], [candidate1, candidate3])
        self.assertIn(response.context['others'][1]['candidate'], [candidate1, candidate3])

    def test_post_with_data_single_candidate(self):
        data = {
            "question-0": "0",
            "question-1": "11",
            "question-2": "13",
            "question-id-0": "4",
            "question-id-1": "5",
            "question-id-2": "6"
        }
        url = reverse('soul_mate_detail_view',
            kwargs={
                'slug': self.antofa.slug,
            })
        candidate2 = Candidate.objects.get(id=2)
        candidate3 = Candidate.objects.get(id=3)
        candidate2.taken_positions.all().delete()
        candidate3.taken_positions.all().delete()

        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed("elections/soulmate_response.html")
        self.assertIn("election", response.context)
        self.assertEquals(response.context["election"], self.antofa)
        self.assertIn("winner", response.context)

    def test_post_with_data_no_candidates(self):
        data = {
            "question-0": "0",
            "question-1": "11",
            "question-2": "13",
            "question-id-0": "4",
            "question-id-1": "5",
            "question-id-2": "6"
        }
        url = reverse('soul_mate_detail_view',
            kwargs={
                'slug': self.antofa.slug,
            })
        candidate1 = Candidate.objects.get(id=1)
        candidate2 = Candidate.objects.get(id=2)
        candidate3 = Candidate.objects.get(id=3)
        candidate1.taken_positions.all().delete()
        candidate2.taken_positions.all().delete()
        candidate3.taken_positions.all().delete()

        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed("elections/soulmate_response.html")
        self.assertIn("election", response.context)
        self.assertEquals(response.context["election"], self.antofa)
        self.assertNotIn("winner", response.context)
        self.assertIn("others", response.context)
        self.assertFalse(response.context['others'])

    def test_post_with_data_exclude_not_answering_candidates(self):
        data = {
            "question-0": "0",
            "question-1": "11",
            "question-2": "13",
            "question-id-0": "4",
            "question-id-1": "5",
            "question-id-2": "6"
        }
        url = reverse('soul_mate_detail_view',
            kwargs={
                'slug': self.antofa.slug,
            })
        # candidate2 hasn't answered anything
        candidate2 = Candidate.objects.get(id=2)
        candidate2.taken_positions.all().delete()

        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed("elections/soulmate_response.html")
        self.assertIn("election", response.context)
        self.assertEquals(response.context["election"], self.antofa)
        self.assertNotIn("winner", response.context)
        self.assertIn("others", response.context)
        for c in response.context['others']:
            if c['candidate'] == candidate2:
                self.fail(u"A candidate without answers is in the response")
        self.assertTrue(True)



    def test_if_no_taken_position_provided(self):
        '''If there is no taken prosition provided'''
        data = {
            "question-0": "8",
            "question-1": "0",  # This data is missing
            "question-2": "13",
            "question-id-0": "4",
            "question-id-1": "5",
            "question-id-2": "6"
        }
        url = reverse('soul_mate_detail_view',
            kwargs={
                'slug': self.antofa.slug,
            })

        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
