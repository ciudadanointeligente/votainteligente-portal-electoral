# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.models import Candidate, NON_WHITE_KEY, NON_MALE_KEY
from merepresenta.tests.volunteers import VolunteersTestCaseBase
from backend_candidate.models import CandidacyContact, Candidacy
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
import mock
from django.views.generic.edit import FormView
from django.core import mail
from merepresenta.models import VolunteerInCandidate, VolunteerGetsCandidateEmailLog, Candidate
from merepresenta.voluntarios.models import VolunteerProfile
from elections.models import PersonalData, Area, Election
from django.conf import settings
import datetime
from merepresenta.candidatos.forms import CPFAndDdnForm, CPFAndDdnForm2
from django.core import mail

PASSWORD = 'candidato123'


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class CandidateLoginView(VolunteersTestCaseBase):
    def setUp(self):
        super(CandidateLoginView, self).setUp()
        session = self.client.session
        session['facebook_state'] = '1'
        session.save()

    def atest_get_cpf_and_date_view(self):
        url = reverse('cpf_and_date_2')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('form', response.context)



@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class CandidateLoginView(VolunteersTestCaseBase):
    def setUp(self):
        super(CandidateLoginView, self).setUp()
        session = self.client.session
        session['facebook_state'] = '1'
        session.save()

    def test_get_login(self):
        url = reverse('candidate_login')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_if_user_is_logged_in_but_not_candidate_and_not_volunteer_then_go_to_cpf(self):
        url = reverse('candidate_login')
        user = User.objects.create_user(username="candidate", password=PASSWORD)
        self.client.login(username=user.username, password=PASSWORD)
        response = self.client.get(url)
        cpf_and_date_url = reverse('cpf_and_date2')
        self.assertRedirects(response, cpf_and_date_url)

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
class CPFChoosingView2(VolunteersTestCaseBase):
    def setUp(self):
        super(CPFChoosingView2, self).setUp()
        self.d = datetime.datetime(2009, 10, 5, 18, 00)
        self.area = Area.objects.create(name="area")
        self.election = Election.objects.create(name='ele', area=self.area)
        self.candidate = Candidate.objects.create(name='THE candidate', cpf='1234', data_de_nascimento=self.d)
        self.election.candidates.add(self.candidate)
        session = self.client.session
        session['facebook_state'] = '1'
        session['facebook_slug'] = self.candidate.slug
        session.save()

    def test_form_for_joining_a_user_and_a_candidate(self):
        user = User.objects.create(username='HolaSoyCandidato')
        data = {
            'nascimento': self.d,
            'cpf': '1234',
            }
        form = CPFAndDdnForm2(data=data)
        self.assertTrue(form.is_valid())
        candidate = form.get_candidate()
        self.assertEquals(candidate, self.candidate)

    def test_form_valid(self):
        data = {
            'nascimento': self.d,
            'cpf': '12-34',
            }
        
        form = CPFAndDdnForm2(data=data)
        self.assertTrue(form.is_valid())
        candidate = form.get_candidate()
        self.assertEquals(candidate, self.candidate)

    def test_get_the_view(self):
        url = reverse('cpf_and_date2')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CPFAndDdnForm2)

    def test_trying_to_get_to_cpf_and_data_view_is_not_possible_for_volunteers(self):
        user = User.objects.create_user(username="volunteer", password=PASSWORD, is_staff=True)

        url = reverse('cpf_and_date2')
        self.client.login(username=user.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_post_to_the_view_returns_login_for_candidate(self):
        url = reverse('cpf_and_date2')
        data = {
            'nascimento': self.d.strftime('%d/%m/%Y'),
            'cpf': '1234',
            }
        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'candidatos/login_with_facebook.html')
        self.assertEquals(response.context['candidate'], self.candidate)

    @override_settings(SOCIAL_AUTH_FACEBOOK_KEY='1',
                       SOCIAL_AUTH_FACEBOOK_SECRET='2')
    @mock.patch('social_core.backends.base.BaseAuth.request')
    def test_complete_with_facebook(self, mock_request):
        
        url = reverse('candidate_social_complete', kwargs={'backend': 'facebook'})
        url += '?code=2&state=1'
        mock_request.return_value.json.return_value = {'access_token': '123'}
        with mock.patch('django.contrib.sessions.backends.base.SessionBase.set_expiry', side_effect=[OverflowError, None]):
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 302)
            social_user = UserSocialAuth.objects.get()
            created_user = social_user.user
            self.assertFalse(created_user.is_staff)

    def test_candidacy_created_redirects(self):
        url_complete_profile = reverse('merepresenta_complete_profile', kwargs={'slug': self.election.slug,
                                                                                     'candidate_slug': self.candidate.slug})
        user = User.objects.create_user(username='HolaSoyCandidato', password=PASSWORD)
        candidacy = Candidacy.objects.create(candidate=self.candidate, user=user)
        url = reverse('cpf_and_date2')
        self.client.login(username=user.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertRedirects(response, url_complete_profile)

    def test_email_sent_to_volunteer(self):
        volunteer = User.objects.create(username="volunteer")
        volunteer.email = 'the_one@voluntarias.org.br'
        volunteer.save()
        VolunteerGetsCandidateEmailLog.objects.create(volunteer=volunteer, candidate=self.candidate)
        user = User.objects.create_user(username='HolaSoyCandidato', password=PASSWORD)
        candidacy = Candidacy.objects.create(candidate=self.candidate, user=user)
        
        self.assertTrue(len(mail.outbox))
        the_mail_to_the_volunteer = mail.outbox[0]
        self.assertIn(volunteer.email, the_mail_to_the_volunteer.to)


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls',
    THEME='merepresenta',
    TEMPLATES=TEMPLATES)
class CPFChoosingView(VolunteersTestCaseBase):
    def setUp(self):
        super(CPFChoosingView, self).setUp()

    def test_form_for_joining_a_user_and_a_candidate(self):
        d = datetime.datetime(2009, 10, 5, 18, 00)
        c = Candidate.objects.create(name='THE candidate', cpf='1234', data_de_nascimento=d)
        user = User.objects.create(username='HolaSoyCandidato')
        data = {
            'nascimento': d,
            'cpf': '1234',
            }
        form = CPFAndDdnForm(data=data, user=user)
        self.assertTrue(form.is_valid())
        candidacy = form.save()
        self.assertEquals(candidacy.candidate, c)
        self.assertEquals(candidacy.user, user)

    def test_form_invalid(self):
        d = datetime.datetime(2009, 10, 5, 18, 00)
        c = Candidate.objects.create(name='THE candidate', cpf='1234', data_de_nascimento=d)
        user = User.objects.create(username='HolaSoyCandidato')
        data = {
            'nascimento': d,
            'cpf': '4321',
            }
        form = CPFAndDdnForm(data=data, user=user)
        self.assertFalse(form.is_valid())

        d = datetime.datetime(2019, 10, 5, 18, 00)
        data = {
            'nascimento': d,
            'cpf': '1234',
            }
        form = CPFAndDdnForm(data=data, user=user)
        self.assertFalse(form.is_valid())

    def test_get_view(self):
        url = reverse('cpf_and_date')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        volunteer = User.objects.create_user(username="voluntario", password=PASSWORD, is_staff=True)
        possible_candidate = User.objects.create_user(username='EuSoCandidato', password=PASSWORD)
        
        self.client.login(username=volunteer.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

        self.client.logout()
        self.client.login(username=possible_candidate.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CPFAndDdnForm)

        # If user has another candidate connected then take it directly to the backend_candidate_home view
        area = Area.objects.create(name="area")
        election = Election.objects.create(name='ele', area=area)
        candidate = Candidate.objects.create(name="Candi")
        election.candidates.add(candidate)
        Candidacy.objects.create(candidate=candidate, user=possible_candidate)
        url_complete_profile = reverse('merepresenta_complete_profile', kwargs={'slug': election.slug, 'candidate_slug': candidate.slug})
        response = self.client.get(url)
        self.assertRedirects(response, url_complete_profile)


    def test_post_to_the_view(self):
        d = datetime.datetime(2009, 10, 5, 18, 00)
        area = Area.objects.create(name="area")
        election = Election.objects.create(name='ele', area=area)
        c = Candidate.objects.create(name='THE candidate', cpf='1234', data_de_nascimento=d)
        election.candidates.add(c)
        data = {
            'nascimento': d.strftime('%d/%m/%Y'),
            'cpf': '1234',
        }
        url = reverse('cpf_and_date')
        possible_candidate = User.objects.create_user(username='EuSoCandidato', password=PASSWORD)
        self.client.login(username=possible_candidate.username, password=PASSWORD)

        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 302)
        candidacy = Candidacy.objects.get(user=possible_candidate)