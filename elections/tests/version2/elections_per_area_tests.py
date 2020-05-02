# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, Area, Candidate, QuestionCategory
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.sites.models import Site
from django.test import override_settings
from django.shortcuts import render
from constance import config
from constance.test import override_config

class ElectionsPerAreaTestCase(TestCase):
    def test_an_election_can_have_an_area(self):
        argentina = Area.objects.create(name=u'Argentina', slug='argentina')
        election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            area=argentina,
            extra_info_content=u'Más Información')

        self.assertIn(election, argentina.elections.all())

    def test_there_is_a_url_with_the_area(self):
        argentina = Area.objects.create(name=u'Argentina', slug='argentina')
        url = argentina.get_absolute_url()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/area.html')

    def test_candidates_per_area(self):
        argentina = Area.objects.create(name=u'Argentina', slug='argentina')
        election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            area=argentina,
            extra_info_content=u'Más Información')
        c1 = Candidate.objects.create(name='Candidate1')
        c2 = Candidate.objects.create(name='Candidate2')
        c3 = Candidate.objects.create(name='Candidate3')
        election.candidates.add(c1)
        election.candidates.add(c2)
        self.assertIn(c1, argentina.candidates().all())
        self.assertIn(c2, argentina.candidates().all())
        self.assertNotIn(c3, argentina.candidates().all())

    def test_area_ranking(self):
        argentina = Area.objects.create(name=u'Argentina', slug='argentina')
        election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            area=argentina,
            extra_info_content=u'Más Información')
        c1 = Candidate.objects.create(name='Candidate1')
        c2 = Candidate.objects.create(name='Candidate2')
        c3 = Candidate.objects.create(name='Candidate3')
        election.candidates.add(c1)
        election.candidates.add(c2)
        self.assertIn(c1, election.ranking().all())
        self.assertIn(c2, election.ranking().all())
        self.assertNotIn(c3, election.ranking().all())

    def test_get_position_in_ranking(self):
        argentina = Area.objects.create(name=u'Argentina', slug='argentina')
        election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            area=argentina,
            extra_info_content=u'Más Información')
        c1 = Candidate.objects.create(name='Candidate1')
        c2 = Candidate.objects.create(name='Candidate2')
        c3 = Candidate.objects.create(name='Candidate3')
        election.candidates.add(c1)
        election.candidates.add(c2)
        self.assertIsNotNone(election.position_in_ranking(c1))
        self.assertIsNotNone(election.position_in_ranking(c2))
        self.assertIsNone(election.position_in_ranking(c3))

        position_c1 = c1.ranking_in_election()
        position_c2 = c2.ranking_in_election()
        position_c3 = c3.ranking_in_election()

        self.assertIsNone(position_c3)
        self.assertEquals(position_c1, election.position_in_ranking(c1))
        self.assertEquals(position_c2, election.position_in_ranking(c2))

    def test_get_position_no_questions(self):
        QuestionCategory.objects.all().delete()
        argentina = Area.objects.create(name=u'Argentina', slug='argentina')

        election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            area=argentina,
            extra_info_content=u'Más Información')
        c1 = Candidate.objects.create(name='Candidate1')
        c2 = Candidate.objects.create(name='Candidate2')
        c3 = Candidate.objects.create(name='Candidate3')
        election.candidates.add(c1)
        election.candidates.add(c2)
        self.assertIsNotNone(election.position_in_ranking(c1))
        self.assertIsNotNone(election.position_in_ranking(c2))
        self.assertIsNone(election.position_in_ranking(c3))

        position_c1 = c1.ranking_in_election()
        position_c2 = c2.ranking_in_election()
        position_c3 = c3.ranking_in_election()

        self.assertIsNone(position_c3)
        self.assertEquals(position_c1, election.position_in_ranking(c1))
        self.assertEquals(position_c2, election.position_in_ranking(c2))

    @override_config(DEFAULT_AREA='argentina')
    def test_area_index_view(self):
        argentina = Area.objects.create(name=u'Argentina', slug='argentina')
        election = Election.objects.create(
            name='the name',
            area=argentina)
        url = reverse('know_your_candidates')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['default_election'])

    def test_area_index_view_if_not_default_area(self):
        argentina = Area.objects.create(name=u'Argentina', slug='argentina')
        election = Election.objects.create(
            name='the name',
            area=argentina)
        url = reverse('know_your_candidates')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['default_election'])

    @override_config(SHOW_ALL_CANDIDATES_IN_THIS_ORDER='senador, diputado', DEFAULT_AREA='argentina')
    def test_get_all_candidates_if_show_all_candidates_is_true(self):
        first_e = Election.objects.get(id=1)
        first_e.position = 'diputado'
        first_e.save()
        second_e = Election.objects.get(id=2)
        second_e.position = 'senador'
        second_e.save()
        argentina = Area.objects.create(name=u'Argentina', slug='argentina')
        election = Election.objects.create(
            name='the name',
            area=argentina)
        url = reverse('know_your_candidates')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('positions', response.context)
        self.assertEquals(response.context['positions'][0]['name'], 'senador')
        for c in second_e.candidates.all():
            self.assertIn(c, response.context['positions'][0]['candidates'])
        self.assertEquals(response.context['positions'][1]['name'], 'diputado')
        for c in first_e.candidates.all():
            self.assertIn(c, response.context['positions'][1]['candidates'])

    def test_get_area_parents(self):
        child = Area.objects.create(name="children")
        mother = Area.objects.create(name="mother")
        mother.children.add(child)
        grand_mother = Area.objects.create(name="grand_mother")
        grand_mother.children.add(mother)

        self.assertIn(grand_mother, child.parents)
        self.assertIn(mother, child.parents)


    def test_get_area_parents_prevent_cicles(self):
        child = Area.objects.create(name="children")
        mother = Area.objects.create(name="mother")
        mother.children.add(child)
        child.children.add(mother)

        self.assertEquals(len(child.parents), 2)

    @override_settings(FILTERABLE_AREAS_TYPE = ['Comuna'])
    def test_areas_redirect_when_necesary(self):
        child = Area.objects.create(name="children", classification="Comuna", slug='children')
        mother = Area.objects.create(name="mother", slug='mother')
        mother.children.add(child)

        url = child.get_absolute_url()
        response = self.client.get(url)
        url_mother = mother.get_absolute_url()
        self.assertRedirects(response, url_mother)

        child2 = Area.objects.create(name="children", classification="Comuna", slug='children2')
        url = child2.get_absolute_url()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    @override_settings(FILTERABLE_AREAS_TYPE = ['Comuna'])
    def test_related_areas_elections(self):
        child = Area.objects.create(name="children", classification="Comuna", slug='children')
        mother = Area.objects.create(name="mother", slug='mother')
        mother.children.add(child)

        Election.objects.create(name='the election_mother',
                                description='this is a description',
                                extra_info_title=u'ver más',
                                area=mother,
                                position='alcalde',
                                extra_info_content=u'Más Información')

        grand_mother = Area.objects.create(name="grand_mother", slug='grand-mother')
        grand_mother.children.add(mother)

        Election.objects.create(name='the election_grand_mother',
                                description='this is a description',
                                extra_info_title=u'ver más',
                                area=grand_mother,
                                position='alcalde',
                                extra_info_content=u'Más Información')

        # assertions
        related_to_mother = mother.get_related()
        self.assertIn(grand_mother, related_to_mother)
        related_to_grand_mother = grand_mother.get_related()
        self.assertIn(mother, related_to_grand_mother)
        comunas = mother.get_containing_filterable_areas()
        self.assertIn(child, comunas)

class AreaOGPTestCase(TestCase):
    def setUp(self):
        self.argentina = Area.objects.create(name=u'Argentina', slug='argentina')
        self.site = Site.objects.get_current()

    def test_get_absolute_url(self):
        url = reverse('area', kwargs={'slug': self.argentina.slug})
        self.assertEquals(url, self.argentina.get_absolute_url())

    def test_ogp_things(self):
        self.assertIn(self.argentina.name, self.argentina.ogp_title())
        self.assertEquals('website', self.argentina.ogp_type())
        expected_url = "http://%s%s" % (self.site.domain,
                                        self.argentina.get_absolute_url())
        self.assertEquals(expected_url, self.argentina.ogp_url())
        expected_url = "http://%s%s" % (self.site.domain,
                                        static('img/logo_vi_og.jpg'))
        self.assertEquals(expected_url, self.argentina.ogp_image())

    def test_area_elections_without_position(self):
        election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            area=self.argentina,
            position='alcalde',
            extra_info_content=u'Más Información')

        elections_without_position = self.argentina.elections_without_position.all()
        self.assertNotIn(election, elections_without_position)
        self.assertIn(election, self.argentina.elections.all())
