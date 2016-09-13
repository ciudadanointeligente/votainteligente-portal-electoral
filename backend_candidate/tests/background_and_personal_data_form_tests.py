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
from popolo.models import ContactDetail


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
        self.data = {'age': 4,
                     'party': 'Partido chilote',
                     'image': self.get_image(),
                     'program_link': 'www.pdf995.com/samples/pdf.pdf',
                     'facebook': 'https://www.facebook.com/PabloMoyaConcejal/',
                     'twitter': 'https://www.twitter.com/Pablo_Moya',
                     'url': 'https://google.cl'}

    def test_candidate_form(self):
        
        form_class = get_candidate_profile_form_class()
        form = form_class(candidate=self.candidate,
                          data=self.data)
        self.assertTrue(form.is_valid())
        self.assertIn('age', form.cleaned_data.keys())
        self.assertEquals(form.cleaned_data['age'], self.data['age'])
        self.assertEquals(form.cleaned_data['party'], self.data['party'])

        form.save()
        personal_datas = PersonalData.objects.filter(candidate=self.candidate)
        self.assertEquals(len(personal_datas), 3)
        age = personal_datas.get(value=self.data['age'])
        self.assertEquals(age.label, 'age')
        party = personal_datas.get(value=self.data['party'])
        self.assertEquals(party.label, 'party')
        program = personal_datas.get(label='program_link')
        self.assertTrue(program.value)
        facebook = self.candidate.contact_details.get(contact_type='FACEBOOK')
        self.assertEquals(facebook.value, self.data['facebook'])
        facebook = self.candidate.contact_details.get(contact_type='TWITTER')
        self.assertEquals(facebook.value, self.data['twitter'])
        facebook = self.candidate.contact_details.get(contact_type='URL')
        self.assertEquals(facebook.value, self.data['url'])

        form.save()
        personal_datas = PersonalData.objects.filter(candidate=self.candidate)
        self.assertEquals(personal_datas.count(), 3)

        self.assertEquals(self.candidate.contact_details.count(), 3)
        self.candidate.add_contact_detail(label='perrito',
                                          contact_type="FACEBOOK",
                                          value="http://facebook.com")
        form = form_class(candidate=self.candidate,
                          data=self.data)
        self.assertEquals(form.initial['facebook'], self.data['facebook'])


    def test_template_filter(self):
        personal_data = PersonalData.objects.create(label='age',
                                                    value='perrito chiquitito',
                                                    candidate=self.candidate)
        template = Template("{% load votainteligente_extras %}{% personal_data_label personal_data %}")
        context = Context({'personal_data': personal_data})
        self.assertEqual(template.render(context), u'Edad')

    def test_get_12_naranja_brings_the_form(self):
        election = Election.objects.get(id=2)
        url = reverse('backend_candidate:complete_profile',
                      kwargs={'slug': election.slug,
                              'candidate_id': self.candidate.id})
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        form_class = get_candidate_profile_form_class()
        for field in form_class.base_fields:
            self.assertIn(field, response.context['form'].fields)
        form = form_class(data=self.data,
                          candidate=self.candidate)
        self.assertTrue(form.is_valid())
        form.save()
        response = self.client.get(url)
        form = response.context['form']
        self.assertEquals(form.initial['age'], str(self.data['age']))
        self.assertEquals(form.initial['party'], self.data['party'])
        self.assertEquals(form.initial['facebook'], self.data['facebook'])
        self.assertEquals(form.initial['twitter'], self.data['twitter'])
        self.assertEquals(form.initial['url'], self.data['url'])

    def test_get_complete_profile_with_crossed_candidates(self):
        fiera_user = User.objects.get(username='fiera')
        election = Election.objects.get(id=2)
        fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!')
        election.candidates.add(fiera_candidata)
        Candidacy.objects.create(candidate=fiera_candidata,
                                 user=fiera_user)
        url = reverse('backend_candidate:complete_profile',
                      kwargs={'slug': election.slug,
                              'candidate_id': fiera_candidata.id})
        # Feli is not member of the candidacy of fiera
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)

        self.assertEquals(response.status_code, 404)


    def test_view_post_data(self):
        election = Election.objects.get(id=2)
        self.client.login(username=self.feli,
                          password='alvarez')
        url = reverse('backend_candidate:complete_profile',
                      kwargs={'slug': election.slug,
                              'candidate_id': self.candidate.id})
        data = self.data
        response = self.client.post(url,
                                    data=data)
        self.assertRedirects(response, url)
        personal_datas = PersonalData.objects.filter(candidate=self.candidate)
        self.assertTrue(len(personal_datas), 2)
        age = personal_datas.get(value=self.data['age'])
        self.assertEquals(age.label, 'age')
        party = personal_datas.get(value=self.data['party'])
        self.assertEquals(party.label, 'party')
        candidate = Candidate.objects.get(id=self.candidate.id)
        self.assertTrue(candidate.image)

        # Doing it twice
        response = self.client.post(url,
                                    data=data)
        party = PersonalData.objects.filter(candidate=self.candidate,
                                            label='party')
        self.assertEquals(len(party), 1)
