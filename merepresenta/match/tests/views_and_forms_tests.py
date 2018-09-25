# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.match.forms import QuestionsCategoryForm
from merepresenta.match.tests.match_tests import MeRepresentaMatchBase
from merepresenta.models import LGBTQDescription
from django.core.urlresolvers import reverse
from elections.models import Election, Area
import json
from django.utils.text import slugify



@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class QuestionCategoryForm(TestCase, MeRepresentaMatchBase):
    def setUp(self):
        super(QuestionCategoryForm, self).setUp()
        self.set_data()

    def test_instanciate_form(self):
        a = Area.objects.create(name='area')
        data = {'categories': [self.cat1.id, self.cat2.id], 'area': a}
        form = QuestionsCategoryForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertIn(self.cat1, form.cleaned_data['categories'])
        self.assertIn(self.cat2, form.cleaned_data['categories'])
        self.assertEquals(a, form.cleaned_data['area'])

    def test_get_the_view(self):
        url = reverse('match')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response.context['form'], QuestionsCategoryForm)

    def test_get_post(self):
        a = Area.objects.create(name='area')
        e = Election.objects.create(name='Deputada/o estadual', area=a)
        gay = LGBTQDescription.objects.create(name="Gay")
        url = reverse('match')
        data = {'categories': [self.cat1.id, self.cat2.id]}
        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'match/resultado_ajax.html')
        self.assertIn(self.cat1, response.context['categories'])
        self.assertIn(self.cat2, response.context['categories'])
        self.assertIsInstance(response.context['form'], QuestionsCategoryForm)
        election_types = response.context['election_types']

        self.assertEquals(election_types[0]['id'], slugify(e.name))
        self.assertEquals(election_types[0]['label'], e.name)

        lgbt_descriptions = response.context['lgbt_descriptions']
        self.assertEquals(lgbt_descriptions[0]['id'], 'lgbt_' + str(gay.id))
        self.assertEquals(lgbt_descriptions[0]['label'], gay.name)

    def test_post_get_result(self):
        a = Area.objects.create(name='area')
        e = Election.objects.create(name='Deputada/o estadual', area=a)
        gay = LGBTQDescription.objects.create(name="Gay")
        url = reverse('match_result')
        data = {'categories': [self.cat1.id, self.cat2.id], 'area': a}
        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'match/resultado_ajax.html')
        self.assertIn(self.cat1, response.context['categories'])
        self.assertIn(self.cat2, response.context['categories'])
        self.assertEquals(a, response.context['area'])

    def test_post_ajax_result(self):
        url = reverse('match_result_ajax')
        data = {'categories[]': [self.cat1.id, self.cat2.id]}
        response = self.client.post(url, data=data)
        c_as_dict = json.dumps(response.content)
        self.assertTrue(c_as_dict)
