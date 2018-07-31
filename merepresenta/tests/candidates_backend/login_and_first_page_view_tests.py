# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.models import Candidate, NON_WHITE_KEY, NON_MALE_KEY
from merepresenta.tests.volunteers import VolunteersTestCaseBase
from backend_candidate.models import CandidacyContact
from elections.models import PersonalData, Area
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
import mock
from django.views.generic.edit import FormView
from django.core import mail
from merepresenta.models import VolunteerInCandidate, VolunteerGetsCandidateEmailLog, Candidate
from merepresenta.voluntarios.models import VolunteerProfile
from elections.models import Election, Area
from django.conf import settings
import datetime

PASSWORD = 'candidato123'

@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class CandidateLoginView(VolunteersTestCaseBase):
    def setUp(self):
        super(CandidateLoginView, self).setUp()
        session = self.client.session
        session['facebook_state'] = '1'
        session.save()

    # def test_get_login(self):
    #     url = reverse('candidate_login')
    #     response = self.client.get(url)
    #     self.assertEquals(response.status_code, 200)


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class CPFChoosingView(VolunteersTestCaseBase):
    def setUp(self):
        super(CPFChoosingView, self).setUp()


    def test_ask_for_cpf_view(self):
        url = reverse('candidate_cpf')
        user = User.objects.create_user(username="candidato", password=PASSWORD)
        self.client.login(username=user.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    # def test_post_to_the_view(self):
    #     d = datetime.datetime(2009, 10, 5, 18, 00)
    #     c = Candidate.objects.create(name='THE candidate', cpf='1234', )
    #     data = {

    #     }
    #     # self.assertTrue(response.context['form'])

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