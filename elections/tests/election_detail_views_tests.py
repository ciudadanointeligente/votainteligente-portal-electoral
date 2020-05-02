# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, QuestionCategory
from django.core.urlresolvers import reverse
from candidator.models import Topic, Position, TakenPosition


class CandidateInElectionsViewsTestCase(TestCase):
    def setUp(self):
        super(CandidateInElectionsViewsTestCase, self).setUp()
        self.tarapaca = Election.objects.get(id=1)

    def test_url_candidate(self):
        url = reverse('candidate_detail_view', kwargs={
            'election_slug': self.tarapaca.slug,
            'slug': self.tarapaca.candidates.all()[0].id
            })
        self.assertTrue(url)

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

    def test_url_is_reachable_for_one_candidates(self):
        url = reverse('face_to_face_one_candidate_detail_view',
            kwargs={
                'slug': self.tarapaca.slug,
                'slug_candidate_one': self.tarapaca.candidates.all()[0].id,
            })
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/compare_candidates.html')

    def test_url_is_reachable_for_no_one_candidates(self):
        url = reverse('face_to_face_no_candidate_detail_view',
            kwargs={
                'slug': self.tarapaca.slug,
            })
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/compare_candidates.html')

    def test_it_has_a_percentage_of_similitude(self):
        candidate1 = self.tarapaca.candidates.all()[0]
        candidate2 = self.tarapaca.candidates.all()[1]
        categories = QuestionCategory.objects.filter(election=self.tarapaca)
        q_like_fiera = Topic.objects.filter(category__in=categories).get(label="Le gusta la Fiera??")
        you_like_fiera_yes = Position.objects.get(topic=q_like_fiera, label="Si")
        you_like_fiera_no = Position.objects.get(topic=q_like_fiera, label="No")
        tpf1 = TakenPosition.objects.get(person=candidate1, topic=q_like_fiera)
        tpf1.position = you_like_fiera_yes
        tpf1.save()
        tpf2 = TakenPosition.objects.get(person=candidate2, topic=q_like_fiera)
        tpf2.position = you_like_fiera_no
        tpf2.save()
        #this adds 1/3 to the similitude number
        q_like_benito = Topic.objects.filter(category__in=categories).get(label="Le gusta Benito??")
        you_like_benito_yes = Position.objects.get(topic=q_like_benito, label="Si")
        tpb1 = TakenPosition.objects.get(person=candidate1, topic=q_like_benito)
        tpb1.position = you_like_benito_yes
        tpb1.save()
        tpb2 = TakenPosition.objects.get(person=candidate2, topic=q_like_benito)
        tpb2.position = you_like_benito_yes
        tpb2.save()
        #this guys didn't answer the same thing
        #no one has answered this question
        url = reverse('face_to_face_two_candidates_detail_view',
            kwargs={
                'slug': self.tarapaca.slug,
                'slug_candidate_one': candidate1.slug,
                'slug_candidate_two': candidate2.slug,
            })
        response = self.client.get(url)

        self.assertIn('similitude', response.context)

        self.assertEquals(response.context['similitude'], 33)

    def test_it_returns_zero_if_there_are_no_questions(self):

        candidate1 = self.tarapaca.candidates.all()[0]
        candidate2 = self.tarapaca.candidates.all()[1]
        categories = QuestionCategory.objects.filter(election=self.tarapaca)
        Topic.objects.filter(category__in=categories).delete()
        url = reverse('face_to_face_two_candidates_detail_view',
            kwargs={
                'slug': self.tarapaca.slug,
                'slug_candidate_one': candidate1.slug,
                'slug_candidate_two': candidate2.slug,
            })

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        self.assertIn('similitude', response.context)

        self.assertEquals(response.context['similitude'], 0)

    def test_election_has_anyone_answered(self):
        TakenPosition.objects.all().delete()
        self.assertFalse(self.tarapaca.has_anyone_answered())
        c = self.tarapaca.candidates.first()
        topic = self.tarapaca.categories.first().topics.first()
        position = topic.positions.first()
        c.taken_positions.create(topic=topic, position=position)
        self.assertTrue(self.tarapaca.has_anyone_answered())
