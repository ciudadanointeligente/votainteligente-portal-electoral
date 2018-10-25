# coding=utf-8
from backend_candidate.tests import SoulMateCandidateAnswerTestsBase
from django.test import override_settings, modify_settings
from merepresenta.models import Candidate, LGBTQDescription, CandidateQuestionCategory, QuestionCategory
from merepresenta.forms import PersonalDataForm
from backend_candidate.forms import get_candidate_profile_form_class
from backend_candidate.models import Candidacy
from django.contrib.auth.models import User
from elections.models import PersonalData, Election, Area
from django.template import Template, Context
from django.core.urlresolvers import reverse
from popolo.models import ContactDetail
import datetime


PASSWORD = 'pass'


@override_settings(THEME='merepresenta')
class FormTestCase(SoulMateCandidateAnswerTestsBase):

    def setUp(self):
        super(FormTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(PASSWORD)
        self.feli.save()
        self.d = datetime.datetime(2009, 10, 5, 18, 00)
        self.area = Area.objects.create(name="area")
        self.election = Election.objects.create(name='ele', area=self.area)
        self.candidate = Candidate.objects.create(name='THE candidate', cpf='1234', data_de_nascimento=self.d)
        self.candidacy = Candidacy.objects.create(user=self.feli,
                                                  candidate=self.candidate)
        self.gay = LGBTQDescription.objects.create(name="Gay")
        self.bi = LGBTQDescription.objects.create(name="Bi")
        self.data = {'email': 'perrito@chiquitito.cl',
                     'gender': 'F',
                     'lgbt': True,
                     'lgbt_desc': [self.gay.id, self.bi.id],
                     'bio': u'Ola sou uma pessoa boa em ruim ao mesmo tempo, complexo como os humanos somos, mas qué é bom e qué é ruim?',
                     'candidatura_coletiva': True,
                     'races': ['preta', 'parda'],
                     'renovacao_politica': 'Novo Brasil'}

    def test_candidate_form(self):

        form_class = PersonalDataForm
        form = form_class(candidate=self.candidate,
                          data=self.data)
        self.assertTrue(form.is_valid())
        self.assertIn('email', form.cleaned_data.keys())
        self.assertIn('gender', form.cleaned_data.keys())
        self.assertIn('lgbt', form.cleaned_data.keys())
        self.assertEquals(form.cleaned_data['email'], self.data['email'])
        self.assertEquals(form.cleaned_data['gender'], self.data['gender'])
        self.assertIn(self.data['races'][0], form.cleaned_data['races'])
        form.save()
        self.candidate.refresh_from_db()
        self.assertEquals(self.candidate.gender, self.data['gender'])

        self.assertEquals(self.candidate.email, self.data['email'])
        self.assertEquals(self.candidate.candidatura_coletiva, self.data['candidatura_coletiva'])
        self.assertEquals(self.candidate.bio, self.data['bio'])
        self.assertEquals(self.candidate.renovacao_politica, self.data['renovacao_politica'])


        self.assertTrue(self.candidate.preta)
        self.assertTrue(self.candidate.parda)
        personal_datas = PersonalData.objects.filter(candidate=self.candidate)

        self.assertEquals(len(personal_datas), 0)

    def test_candidate_after(self):
        form_class = PersonalDataForm
        form = form_class(candidate=self.candidate,
                          data=self.data)
        form.is_valid()
        form.save()
        ## ONCE
        form_class = PersonalDataForm
        self.candidate.refresh_from_db()
        form = form_class(candidate=self.candidate)
        self.assertEquals(form.initial['gender'], self.candidate.gender)
        self.assertEquals(form.initial['email'], self.candidate.email)
        self.assertEquals(form.initial['lgbt'], self.candidate.lgbt)
        self.assertEquals(form.initial['bio'], self.candidate.bio)
        self.assertEquals(form.initial['candidatura_coletiva'], self.candidate.candidatura_coletiva)
        self.assertEquals(form.initial['renovacao_politica'], self.candidate.renovacao_politica)
        self.assertTrue(self.candidate.lgbt_desc.all())

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'merepresenta/templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'constance.context_processors.config',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                #'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls',
    THEME='merepresenta',
    TEMPLATES=TEMPLATES)
class GetAndPostToTheUpdateProfileView(SoulMateCandidateAnswerTestsBase):
    def setUp(self):
        super(GetAndPostToTheUpdateProfileView, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(PASSWORD)
        self.feli.save()
        self.d = datetime.datetime(2009, 10, 5, 18, 00)
        self.area = Area.objects.create(name="area")
        self.election = Election.objects.create(name='ele', area=self.area)
        self.candidate = Candidate.objects.create(name='THE candidate', cpf='1234', data_de_nascimento=self.d)
        self.candidacy = Candidacy.objects.create(user=self.feli,
                                                  candidate=self.candidate)
        self.gay = LGBTQDescription.objects.create(name="Gay")
        self.bi = LGBTQDescription.objects.create(name="Bi")
        self.data = {'email': 'perrito@chiquitito.cl',
                     'gender': 'F',
                      'lgbt': True,
                     'bio': u'Ola sou uma pessoa boa em ruim ao mesmo tempo, complexo como os humanos somos, mas qué é bom e qué é ruim?',
                     'candidatura_coletiva': True,
                     'races': ['preta', 'parda'],
                     'renovacao_politica': 'Novo Brasil'}

    def test_get_the_view(self):
        kwargs = {'slug': self.election.slug, 'candidate_slug': self.candidate.slug}
        url = reverse('merepresenta_complete_profile', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
        other_user = User.objects.create_user(username="other_user", password=PASSWORD)
        self.client.login(username=other_user.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

        self.client.login(username=self.feli.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['form'])
        self.assertEquals(response.context['form'].candidate, self.candidate)

    @override_settings(MEREPRESENTA_CANDIDATES_ALLOWED_TO_UPDATE=False)
    def test_if_officially_not_allowed(self):
        '''
        If a candidate has answered then it is taken to its profile
        '''
        cat = QuestionCategory.objects.create(name="Pautas LGBT")
        instance = CandidateQuestionCategory.objects.create(candidate=self.candidate, category=cat)

        kwargs = {'slug': self.election.slug, 'candidate_slug': self.candidate.slug}
        url = reverse('merepresenta_complete_profile', kwargs=kwargs)
        response = self.client.get(url)
        self.assertRedirects(response, self.candidate.get_absolute_url())

    def test_post_to_the_view(self):
        kwargs = {'slug': self.election.slug, 'candidate_slug': self.candidate.slug}
        url = reverse('merepresenta_complete_profile', kwargs=kwargs)
        self.client.login(username=self.feli.username, password=PASSWORD)
        self.assertFalse(self.candidate.gender)
        response = self.client.post(url, data=self.data)
        self.assertRedirects(response, reverse('complete_pautas'))
        self.candidate.refresh_from_db()
        self.assertTrue(self.candidate.gender)

    def test_post_to_the_view_and_then_get_it_again(self):
        kwargs = {'slug': self.election.slug, 'candidate_slug': self.candidate.slug}
        url = reverse('merepresenta_complete_profile', kwargs=kwargs)
        self.client.login(username=self.feli.username, password=PASSWORD)
        self.client.post(url, data=self.data)
        response = self.client.get(url)
        form = response.context['form']
        self.assertIn('gender', form.initial)
        self.assertIn('email', form.initial)
