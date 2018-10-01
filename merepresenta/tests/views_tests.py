# coding=utf-8
from medianaranja2.tests.adapter_tests import MediaNaranjaAdaptersBase
from django.test import TestCase, override_settings
from django.core.urlresolvers import reverse
from merepresenta.forms import MeRepresentaProposalsForm, MeRepresentaQuestionsForm
from django.contrib.sites.models import Site
from popular_proposal.models import (PopularProposalSite)
from merepresenta.models import MeRepresentaPopularProposal, MeRepresentaCommitment, Coaligacao
from elections.models import Area
from django.conf import settings
from unittest import skip
from elections.models import Candidate, Election, QuestionCategory

@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class StandAloneSite(TestCase):
    def test_get_index(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class CandidateDetailView(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(CandidateDetailView, self).setUp()
        self.area = Area.objects.create(name=u"children",
                                        id=u'20',
                                        classification=settings.FILTERABLE_AREAS_TYPE[0])
        self.election = Election.objects.create(name=u'election for children', area=self.area)
        self.candidate = Candidate.objects.create(name=u"name")
        self.election.candidates.add(self.candidate)

    def test_get_candidate_detail(self):
        url = reverse('candidate_detail_view', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')

@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls', DEFAULT_AREA='21')
class MeiaLaranjaAdapterTestCase(MediaNaranjaAdaptersBase):
    popular_proposal_class = MeRepresentaPopularProposal
    commitment_class = MeRepresentaCommitment
    def setUp(self):
        super(MeiaLaranjaAdapterTestCase, self).setUp()
        self.site = Site.objects.create(domain='merepresenta.127.0.0.1.xip.io', name='merepresenta')
        self.setUpProposals()
        self.area = Area.objects.create(name=u"children",
                                        id=u'20',
                                        classification=settings.FILTERABLE_AREAS_TYPE[0])
        self.mother_of_all_areas = Area.objects.create(name=u"mother",
                                                       id=u'21',
                                                       classification='country')
        self.area.parent = self.mother_of_all_areas
        self.area.save()

@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls', DEFAULT_AREA='21')
class MeiaLaranjaTestCase(MediaNaranjaAdaptersBase):
    popular_proposal_class = MeRepresentaPopularProposal
    commitment_class = MeRepresentaCommitment
    def setUp(self):
        super(MeiaLaranjaTestCase, self).setUp()
        self.site = Site.objects.create(domain='merepresenta.127.0.0.1.xip.io', name='merepresenta')
        self.setUpProposals()
        PopularProposalSite.objects.create(popular_proposal=self.p1, site=self.site)
        PopularProposalSite.objects.create(popular_proposal=self.p3, site=self.site)
        self.area = Area.objects.create(name=u"children",
                                        id=u'20',
                                        classification=settings.FILTERABLE_AREAS_TYPE[0])
        self.mother_of_all_areas = Area.objects.create(name=u"mother",
                                                       id=u'21',
                                                       classification='country')
        self.area.parent = self.mother_of_all_areas
        self.area.save()

    def test_get_questionary(self):
        with override_settings(MEREPRESENTA_SITE_ID=self.site.id):
            response = self.client.get(reverse('questionary'))
            self.assertEquals(response.status_code, 200)
            form = response.context['form']
            self.assertIsInstance(form, MeRepresentaProposalsForm)
            proposals_qs = form.fields['proposals'].queryset
            self.assertIn(self.p1, proposals_qs.all())
            self.assertIn(self.p3, proposals_qs.all())
            self.assertNotIn(self.p2, proposals_qs.all())
            areas_qs = form.fields['area'].queryset
            self.assertIn(self.area, areas_qs.all())

    def test_post_questionary(self):
        # MeRepresentaCommitment.objects.create
        election = Election.objects.create(name=u'election for children', area=self.area)
        candidate = Candidate.objects.create(name=u"name")
        election.candidates.add(candidate)
        MeRepresentaCommitment.objects.create(proposal=self.p1, candidate=candidate, commited=True)
        with override_settings(MEREPRESENTA_SITE_ID=self.site.id):
            response = self.client.get(reverse('questionary'))
            management_form_current_step_slug = response.context['wizard']['management_form'].prefix + '-current_step'
            data = {
                management_form_current_step_slug: 0,
                '0-proposals': [self.p1.id, self.p3.id],
                '0-area': self.area.id
            }
            response = self.client.post(reverse('questionary'), data=data)
            self.assertEquals(response.status_code, 200)
            self.assertNotIn('form', response.context.keys())
            self.assertTrue(response.context['results'][0]['candidates'][0]['value'])


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls', DEFAULT_AREA='21')
class AnotherQuestionaryTestCase(MediaNaranjaAdaptersBase):
    def setUp(self):
        QuestionCategory.objects.all().delete()
        super(AnotherQuestionaryTestCase, self).setUp()
        self.site = Site.objects.create(domain='merepresenta.127.0.0.1.xip.io', name='merepresenta')
        self.setUpQuestions()
        self.area = Area.objects.create(name=u"children",
                                        id=u'20',
                                        classification=settings.FILTERABLE_AREAS_TYPE[0])
        self.mother_of_all_areas = Area.objects.create(name=u"mother",
                                                       id=u'21',
                                                       classification='country')
        self.area.parent = self.mother_of_all_areas
        self.area.save()
        QuestionCategory.objects.all().update(election=None)


    def test_get_questionary(self):
        response = self.client.get(reverse('questions'))
        self.assertEquals(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, MeRepresentaQuestionsForm)

    @skip(u'no está siendo usado')
    def test_post_questionary(self):
        url = reverse('questions')
        response = self.client.get(url)
        management_form_current_step_slug = response.context['wizard']['management_form'].prefix + '-current_step'
        a = Area.objects.get(name=u"Territory")
        a.classification=settings.FILTERABLE_AREAS_TYPE[0]
        a.save()
        data = {
            management_form_current_step_slug: 0,
            u"0-" + self.topic1.slug: self.position1.id,
            u"0-" + self.topic2.slug: self.position3.id,
            u"0-" + self.topic3.slug: self.position5.id,
            u"0-area": a.id
        }

        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertNotIn('form', response.context.keys())
        self.assertTrue(response.context['results'][0]['candidates'][0]['value'])


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class TemplatesViews(MediaNaranjaAdaptersBase):
    def test_get_sobre(self):
        url = reverse('sobre')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class ColigacoesPerAreaViewTestCase(MediaNaranjaAdaptersBase):
    def test_get_the_view(self):
        a = Area.objects.create(name='Area')
        coaligacao = Coaligacao.objects.create(name=u"Coaligacao a",
                                               initials='CA',
                                               number='1234',
                                               area=a,
                                               classification='deputado-estadual')
        url = reverse('coligacoes', kwargs={'slug': a.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(a, response.context['area'])
        self.assertIn(coaligacao, response.context['coligacoes']['deputado-estadual'])