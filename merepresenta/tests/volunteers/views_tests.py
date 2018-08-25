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
from merepresenta.models import VolunteerInCandidate, VolunteerGetsCandidateEmailLog
from merepresenta.voluntarios.models import VolunteerProfile
from elections.models import Election, Area
from merepresenta.voluntarios.forms import VoluntarioCandidateHuntForm
from django.conf import settings


PASSWORD="admin123"

class CandidatesOrderedMixin(object):
    def create_ordered_candidates(self):
        Candidate.objects.filter(id__in=[4, 5]).update(gender=NON_MALE_KEY)
        cs = Candidate.objects.filter(id__in=[4,5])
        self.assertEquals(cs[0].is_women, 1)
        self.assertEquals(cs[1].is_women, 1)
        c = Candidate.objects.get(id=5)
        a = c.election.area
        a.classification = settings.FILTERABLE_AREAS_TYPE[0]
        a.save()
        c.race = NON_WHITE_KEY["possible_values"][0]
        c.save()


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class VolunteersViewsTests(VolunteersTestCaseBase, CandidatesOrderedMixin):
    def setUp(self):
        super(VolunteersViewsTests, self).setUp()


    def test_get_index(self):
        url = reverse('volunteer_index')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        u = User.objects.create_user(username="new_user", password="abc")
        self.client.login(username=u.username, password="abc")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

        u.is_staff = True
        u.save()
        self.create_ordered_candidates()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        candidates = response.context['candidates']
        self.assertEquals(int(candidates[0].id), 5)

    def test_if_candidate_has_contact_is_not_shown(self):
        self.set_desprivilegios_on_candidates()
        c = Candidate.objects.get(id=5)
        c.contacts.create(mail="perrito@gatito.cl")

        url = reverse('volunteer_index')
        u = User.objects.create_user(username="new_user", password="abc", is_staff=True)
        self.client.login(username=u.username, password="abc")
        response = self.client.get(url)
        candidates = response.context['candidates']

        self.assertNotIn(c, candidates)


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class LoginView(VolunteersTestCaseBase):
    def setUp(self):
        super(LoginView, self).setUp()
        session = self.client.session
        session['facebook_state'] = '1'
        session.save()

    def test_get_login(self):
        url = reverse('volunteer_login')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_if_user_is_not_staff_then_get_404(self):
        url = reverse('volunteer_login')
        candidate = User.objects.create_user(username="candidato",
                                             password=PASSWORD,
                                             is_staff=False)
        self.client.login(username=candidate.username, password=PASSWORD)
        response = self.client.get(url)

        self.assertEquals(response.status_code, 404)

    def test_if_im_staff_get_redirected(self):
        url = reverse('volunteer_login')
        volunteer = User.objects.create_user(username="volunteer",
                                             password=PASSWORD,
                                             is_staff=True)
        self.client.login(username=volunteer.username, password=PASSWORD)
        response = self.client.get(url)
        index_url = reverse('volunteer_index') 
        self.assertRedirects(response, index_url)


    @override_settings(SOCIAL_AUTH_FACEBOOK_KEY='1',
                       SOCIAL_AUTH_FACEBOOK_SECRET='2')
    @mock.patch('social_core.backends.base.BaseAuth.request')
    def test_complete_with_facebook(self, mock_request):
        volunteer_index_url = reverse('volunteer_index')
        url = reverse('volunteer_social_complete', kwargs={'backend': 'facebook'})
        url += '?code=2&state=1'
        mock_request.return_value.json.return_value = {'access_token': '123'}
        with mock.patch('django.contrib.sessions.backends.base.SessionBase.set_expiry', side_effect=[OverflowError, None]):
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, volunteer_index_url)
            social_user = UserSocialAuth.objects.get()
            created_user = social_user.user
            self.assertTrue(created_user.is_staff)
            self.assertTrue(created_user.volunteer_profile)
            self.assertIsNone(created_user.volunteer_profile.area)


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class CandidateAddMailView(VolunteersTestCaseBase):
    def setUp(self):
        super(CandidateAddMailView, self).setUp()
        self.volunteer = User.objects.create_user(username="voluntario",
                                                  password=PASSWORD,
                                                  is_staff=True)
        self.candidate = Candidate.objects.get(id=5)
        self.url = reverse('add_mail_to_candidate', kwargs={'id': self.candidate.id})

    def test_get_the_obrigado_view(self):
        url = reverse('obrigado')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        
        user = User.objects.create_user(username="non_volunteer", password=PASSWORD)
        self.client.login(username=user.username, password=PASSWORD)        
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        self.client.logout()
        self.client.login(username=self.volunteer.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


    def test_get_the_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('volunteer_login'), response.url)

        user = User.objects.create_user(username="non_volunteer", password=PASSWORD)
        self.client.login(username=user.username, password=PASSWORD)
        response2 = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('volunteer_login'), response.url)

        self.client.logout()
        self.client.login(username=self.volunteer.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        form = response.context['form']
        self.assertEquals(form.candidate, self.candidate)
        self.assertEquals(form.volunteer, self.volunteer)
        self.assertIsInstance(form, VoluntarioCandidateHuntForm)

        volunteer_in_candidate_record = VolunteerInCandidate.objects.get(volunteer=self.volunteer)
        self.assertEquals(volunteer_in_candidate_record.candidate, self.candidate)

    def test_post_to_the_view(self):
        self.client.login(username=self.volunteer.username, password=PASSWORD)
        data = {
            'facebook': False,
            'tse_email': False,
            'other_email': 'perrito@gatito.com'
        }
        response = self.client.post(self.url, data=data)
        self.assertRedirects(response, reverse('obrigado'))
        self.assertEquals(self.candidate.contacts.count(), 1)
        contact = self.candidate.contacts.last()
        self.assertEquals(contact.mail, data['other_email'])
        # self.assertTrue(len(mail.outbox))
        # mail_to_candidate = mail.outbox[0]
        # self.assertIn(contact.mail, mail_to_candidate.to)

    def test_social_begin_facebook(self):
        url = reverse('voluntarios_social_begin', kwargs={"backend": 'facebook'})


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class CouldNotFindAnything(VolunteersTestCaseBase):
    def setUp(self):
        super(CouldNotFindAnything, self).setUp()
        self.volunteer = User.objects.create_user(username="voluntario",
                                                  password=PASSWORD,
                                                  is_staff=True)
        self.candidate = Candidate.objects.get(id=5)
        self.url = reverse('could_not_find_candidate', kwargs={'id': self.candidate.id})

    def test_get_the_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('volunteer_login'), response.url)

        user = User.objects.create_user(username="non_volunteer", password=PASSWORD)
        self.client.login(username=user.username, password=PASSWORD)
        response2 = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('volunteer_login'), response.url)

        self.client.logout()
        self.client.login(username=self.volunteer.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.candidate.refresh_from_db()
        self.assertTrue(self.candidate.is_ghost)

    def test_candidate_marked_as_ghost_is_not_listed(self):
        # self.create_ordered_candidates()
        self.candidate.is_ghost = True
        self.candidate.save()
        url = reverse('volunteer_index')
        
        u = User.objects.create_user(username="new_user", password="abc", is_staff=True)
        self.client.login(username=u.username, password="abc")
        response = self.client.get(url)
        candidates = response.context['candidates']
        self.assertNotIn(self.candidate, candidates)


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class ContactedThrouFacebook(VolunteersTestCaseBase):
    def setUp(self):
        super(ContactedThrouFacebook, self).setUp()
        self.volunteer = User.objects.create_user(username="voluntario",
                                                  password=PASSWORD,
                                                  is_staff=True)
        self.candidate = Candidate.objects.get(id=5)
        self.url = reverse('facebook_contacted', kwargs={'id': self.candidate.id})

    def test_get_the_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('volunteer_login'), response.url)

        user = User.objects.create_user(username="non_volunteer", password=PASSWORD)
        self.client.login(username=user.username, password=PASSWORD)
        response2 = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('volunteer_login'), response.url)

        self.client.logout()
        self.client.login(username=self.volunteer.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.candidate.refresh_from_db()
        self.assertTrue(self.candidate.facebook_contacted)
        log = VolunteerGetsCandidateEmailLog.objects.get(candidate=self.candidate, volunteer=self.volunteer)
        self.assertTrue(log)
        self.assertIsNone(log.contact)


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class UpdatingAreaOfAVolunteerView(VolunteersTestCaseBase, CandidatesOrderedMixin):
    def setUp(self):
        super(UpdatingAreaOfAVolunteerView, self).setUp()
        self.volunteer = User.objects.create_user(username="voluntario",
                                                  password=PASSWORD,
                                                  is_staff=True)

        self.url = reverse('update_area_of_volunteer')
        self.profile = VolunteerProfile.objects.create(user=self.volunteer)

    def test_get_the_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('volunteer_login'), response.url)

        user = User.objects.create_user(username="non_volunteer", password=PASSWORD)
        self.client.login(username=user.username, password=PASSWORD)
        response2 = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('volunteer_login'), response.url)

        self.client.logout()
        self.client.login(username=self.volunteer.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_post_to_the_view(self):
        area = Area.objects.create(name="area 51")
        data = {
            'area': area.id
        }
        self.client.login(username=self.volunteer.username, password=PASSWORD)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_get_index_brings_the_form(self):
        url = reverse('volunteer_index')

        self.create_ordered_candidates()
        u = User.objects.create_user(username="new_user", password=PASSWORD, is_staff=True)
        self.client.login(username=u.username, password=PASSWORD)
        response = self.client.get(url)
        candidates = response.context['candidates']
        self.assertEquals(int(candidates[0].id), 5)

        self.assertTrue(response.context['update_area_form'])
        form = response.context['update_area_form']
        self.assertEquals(form.instance, u.volunteer_profile)

    def test_get_index_if_has_area_selected_then_filters(self):
        url = reverse('volunteer_index')

        self.create_ordered_candidates()
        u = User.objects.create_user(username="new_user", password=PASSWORD, is_staff=True)
        a = Area.objects.create(name='my-area', classification=settings.FILTERABLE_AREAS_TYPE[0])
        VolunteerProfile.objects.create(user=u, area=a)

        
        self.client.login(username=u.username, password=PASSWORD)
        response = self.client.get(url)
        candidates = response.context['candidates']
        candidate_5 = Candidate.objects.get(id=5)
        self.assertNotIn(candidate_5, candidates)
