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
from merepresenta.candidatos.forms import CPFAndDdnForm

PASSWORD = 'candidato123'

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
        cpf_and_date_url = reverse('cpf_and_date')
        self.assertRedirects(response, cpf_and_date_url)


    @override_settings(SOCIAL_AUTH_FACEBOOK_KEY='1',
                       SOCIAL_AUTH_FACEBOOK_SECRET='2')
    @mock.patch('social_core.backends.base.BaseAuth.request')
    def test_complete_with_facebook(self, mock_request):
        cpf_and_date_url = reverse('cpf_and_date')
        url = reverse('candidate_social_complete', kwargs={'backend': 'facebook'})
        url += '?code=2&state=1'
        mock_request.return_value.json.return_value = {'access_token': '123'}
        with mock.patch('django.contrib.sessions.backends.base.SessionBase.set_expiry', side_effect=[OverflowError, None]):
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, cpf_and_date_url)
            social_user = UserSocialAuth.objects.get()
            created_user = social_user.user
            self.assertFalse(created_user.is_staff)


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
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
        url_complete_profile = reverse('backend_candidate:complete_profile', kwargs={'slug': election.slug, 'candidate_slug': candidate.slug})
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

    # @override_settings(SOCIAL_AUTH_FACEBOOK_KEY='1',
    #                    SOCIAL_AUTH_FACEBOOK_SECRET='2')
    # @mock.patch('social_core.backends.base.BaseAuth.request')
    # def test_complete_with_facebook(self, mock_request):
    #     volunteer_index_url = reverse('volunteer_index')
    #     url = reverse('candidate_social_complete', kwargs={'backend': 'facebook'})
    #     url += '?code=2&state=1'
    #     mock_request.return_value.json.return_value = {'access_token': '123'}
    #     with mock.patch('django.contrib.sessions.backends.base.SessionBase.set_expiry', side_effect=[OverflowError, None]):
    #         response = self.client.get(url)
            
    #         self.assertEqual(response.status_code, 302)
    #         self.assertEqual(response.url, volunteer_index_url)
    #         social_user = UserSocialAuth.objects.get()
    #         created_user = social_user.user
    #         self.assertTrue(created_user.is_staff)
    #         self.assertTrue(created_user.volunteer_profile)
    #         self.assertIsNone(created_user.volunteer_profile.area)