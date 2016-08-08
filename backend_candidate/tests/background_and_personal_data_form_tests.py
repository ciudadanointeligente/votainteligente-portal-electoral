# coding=utf-8
from backend_candidate.tests import SoulMateCandidateAnswerTestsBase
from django.test import override_settings
from elections.models import Candidate
from backend_candidate.forms import get_candidate_profile_form_class
from backend_candidate.models import Candidacy
from django.contrib.auth.models import User
from elections.models import PersonalData, Election
from django.template import Template, Context
from django.core.urlresolvers import reverse
from backend_candidate.forms import get_candidate_profile_form_class


@override_settings(THEME='backend_candidate.tests.theme')
class FormTestCase(SoulMateCandidateAnswerTestsBase):

    def setUp(self):
        super(FormTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password('alvarez')
        self.feli.save()
        self.candidate = Candidate.objects.get(pk=1)
        self.candidacy = Candidacy.objects.create(user=self.feli,
                                                  candidate=self.candidate)

    def test_candidate_form(self):
        data = {'age': 4,
                'party': 'Partido chilote'}
        form_class = get_candidate_profile_form_class()
        form = form_class(candidate=self.candidate,
                          data=data)
        self.assertTrue(form.is_valid())
        self.assertIn('age', form.cleaned_data.keys())
        self.assertEquals(form.cleaned_data['age'], data['age'])
        self.assertEquals(form.cleaned_data['party'], data['party'])

        form.save()
        personal_datas = PersonalData.objects.filter(candidate=self.candidate)
        self.assertTrue(len(personal_datas), 2)
        age = personal_datas.get(value=data['age'])
        self.assertEquals(age.label, 'age')
        party = personal_datas.get(value=data['party'])
        self.assertEquals(party.label, 'party')

    def test_template_filter(self):
        personal_data = PersonalData.objects.create(label='age',
                                                    value='perrito chiquitito',
                                                    candidate=self.candidate)
        template = Template("{% load votainteligente_extras %}{% personal_data_label personal_data %}")
        context = Context({'personal_data': personal_data})
        self.assertEqual(template.render(context), u'Edad')

    def test_get_12_naranja_brings_the_form(self):
        election = Election.objects.get(id=2)
        url = reverse('backend_candidate:complete_12_naranja',
                      kwargs={'slug': election.slug,
                              'candidate_id': self.candidate.id})
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertIn('personal_data_form', response.context)
        form_class = get_candidate_profile_form_class()
        for field in form_class.base_fields:
            self.assertIn(field, response.context['personal_data_form'].fields)

    def test_view_post_data(self):
        election = Election.objects.get(id=2)
        url_12_naranja = reverse('backend_candidate:complete_12_naranja',
                                 kwargs={'slug': election.slug,
                                         'candidate_id': self.candidate.id})
        data = {'age': 4,
                'party': 'Partido chilote'}
        self.client.login(username=self.feli,
                          password='alvarez')
        url = reverse('backend_candidate:complete_personal_data',
                      kwargs={'slug': election.slug,
                              'candidate_id': self.candidate.id})

        response_redirect = self.client.get(url)
        self.assertRedirects(response_redirect, url_12_naranja)

        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        personal_datas = PersonalData.objects.filter(candidate=self.candidate)
        self.assertTrue(len(personal_datas), 2)
        age = personal_datas.get(value=data['age'])
        self.assertEquals(age.label, 'age')
        party = personal_datas.get(value=data['party'])
        self.assertEquals(party.label, 'party')
