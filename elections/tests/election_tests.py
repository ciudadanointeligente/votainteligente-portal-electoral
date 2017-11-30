# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election
from loremipsum import get_paragraphs
from django.core.urlresolvers import reverse
from elections.views import ElectionDetailView
from django.views.generic import DetailView
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.sites.models import Site
from django.template.loader import get_template
from django.template import Context


class ElectionTestCase(TestCase):
    def setUp(self):
        super(ElectionTestCase, self).setUp()

    def test_election_create(self):
        election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            extra_info_content=u'Más Información')

        self.assertEquals(election.name, 'the name')
        self.assertEquals(election.slug, 'the-slug')
        self.assertEquals(election.description, 'this is a description')
        self.assertEquals(election.extra_info_title, u'ver más')
        self.assertEquals(election.extra_info_content, u'Más Información')
        self.assertTrue(election.searchable)
        self.assertFalse(election.highlighted)
        self.assertFalse(election.uses_preguntales)
        self.assertFalse(election.uses_ranking)
        self.assertTrue(election.uses_face_to_face)
        self.assertTrue(election.uses_soul_mate)
        self.assertTrue(election.uses_questionary)
        self.assertFalse(election.position)
        self.assertTrue(election.candidates_can_commit_everywhere)
        self.assertIsNone(election.second_round)

    def test_there_are_no_two_elections_with_the_same_slug(self):
        election1 = Election.objects.create(slug='the-slug')
        election2 = Election.objects.create(slug='the-slug')
        self.assertNotEquals(election1.slug, election2.slug)

    def test_slug_based_on_the_name(self):
        election = Election.objects.create(name='the name')
        self.assertEquals(election.slug, 'the-name')

    def test_description_is_very_long(self):
        paragraphs = get_paragraphs(25)
        lorem_ipsum = ', '.join(paragraphs)
        election = Election.objects.create(
            name='the name',
            description=lorem_ipsum
            )
        self.assertEquals(election.description, lorem_ipsum)

    def test_has_tags(self):
        election = Election.objects.create(
            name='Distrito'
            )
        election.tags.add('providencia', 'valdivia')
        tags = [tag.name for tag in election.tags.all()]

        self.assertIn('providencia', tags)
        self.assertIn('valdivia', tags)

    def test_unicode(self):
        election = Election.objects.create(
            name='Distrito'
            )

        self.assertEquals(election.__unicode__(), election.name)

    def test_get_absolute_url(self):
        election = Election.objects.create(
            name='Distrito',
            slug='distrito'
            )
        expected_url = reverse('election_view', kwargs={'slug': election.slug})

        self.assertEquals(election.get_absolute_url(), expected_url)

    def test_extra_info_reverse_url(self):
        election = Election.objects.create(
            name='Distrito',
            slug='distrito'
            )
        reverse_url = reverse('election_extra_info', kwargs={'slug': election.slug})
        self.assertTrue(reverse_url)

    def test_election_extra_info_url_is_reachable(self):
        election = Election.objects.create(
            name='Distrito',
            slug='distrito'
            )
        reverse_url = reverse('election_extra_info', kwargs={'slug': election.slug})
        response = self.client.get(reverse_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['election'], election)
        self.assertTemplateUsed(response, "elections/extra_info.html")

    def test_get_election_extra_info_url(self):
        election = Election.objects.create(
            name='Distrito',
            slug='distrito'
            )
        expected_url = reverse('election_extra_info', kwargs={'slug': election.slug})

        self.assertEquals(election.get_extra_info_url(), expected_url)

    def test_get_election_card(self):
        election = Election.objects.create(
            name='Distrito',
            slug='distrito'
            )
        template_str = get_template('elections/election_card.html')
        context = {"name": "thename", 'election': election}
        expected_template = template_str.render(context)

        actual_rendered_template = election.card(context=context)

        self.assertEqual(expected_template, actual_rendered_template)


class ElectionExtraInfo(TestCase):
    def test_an_election_has_extra_info(self):
        election = Election.objects.create(name='the name',
                                           slug='the-slug',
                                           description='this is a description',
                                           extra_info_title=u'ver más',
                                           extra_info_content=u'Más Información')
        election.extra_info['ribbon'] = "perrito"
        election.save()
        self.assertEquals(election.extra_info['ribbon'], "perrito")

    def test_election_has_default_info(self):
        election = Election.objects.create(name='the name',
                                           slug='the-slug',
                                           description='this is a description',
                                           extra_info_title=u'ver más',
                                           extra_info_content=u'Más Información')
        self.assertEquals(election.extra_info, settings.DEFAULT_ELECTION_EXTRA_INFO)


class ElectionViewTestCase(TestCase):
    def setUp(self):
        super(ElectionViewTestCase, self).setUp()
        self.election = Election.objects.filter(searchable=True)[0]
        self.site = Site.objects.get_current()

    def test_view_has_model(self):
        view = ElectionDetailView()
        self.assertIsInstance(view, DetailView)
        self.assertEquals(view.model, Election)

    def test_url_is_reachable(self):
        url = reverse('election_view', kwargs={'slug': self.election.slug})
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('election', response.context)
        self.assertTemplateUsed(response, 'elections/election_detail.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_election_ogp(self):
        self.assertIn(self.election.name, self.election.ogp_title())
        self.assertEquals('website', self.election.ogp_type())
        expected_url = "http://%s%s" % (self.site.domain,
                                        self.election.get_absolute_url())
        self.assertEquals(expected_url, self.election.ogp_url())
        expected_url = "http://%s%s" % (self.site.domain,
                                        static('img/logo_vi_og.jpg'))
        self.assertEquals(expected_url, self.election.ogp_image())

    def test_ayudanos_per_election_(self):
        url = reverse('help_election', kwargs={'slug': self.election.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'], self.election)
