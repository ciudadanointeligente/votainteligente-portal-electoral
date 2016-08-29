# coding=utf-8
from backend_candidate.tests import SoulMateCandidateAnswerTestsBase
from elections.models import Candidate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from backend_candidate.models import (Candidacy,
                                      is_candidate,
                                      CandidacyContact,
                                      send_candidate_a_candidacy_link,
                                      send_candidate_username_and_password)
from backend_candidate.forms import get_form_for_election
from backend_candidate.tasks import (let_candidate_now_about_us,
                                     send_candidates_their_username_and_password)
from django.template import Template, Context
from elections.models import Election
from candidator.models import TakenPosition
from django.core import mail
from django.test import override_settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site
from django.core.management import call_command


class CandidacyTestCaseBase(SoulMateCandidateAnswerTestsBase):
    def setUp(self):
        super(CandidacyTestCaseBase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password('alvarez')
        self.feli.save()
        self.candidate = Candidate.objects.get(pk=1)


class CandidacyModelTestCase(CandidacyTestCaseBase):
    def setUp(self):
        super(CandidacyModelTestCase, self).setUp()

    def test_instanciate_candidacy(self):
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        self.assertEquals(candidacy.user, self.feli)
        self.assertEquals(candidacy.candidate, self.candidate)
        self.assertTrue(candidacy.created)
        self.assertTrue(candidacy.updated)

    def test_user_has_candidacy(self):
        self.assertFalse(is_candidate(self.feli))
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        self.assertTrue(is_candidate(self.feli))

    def test_filter_times(self):
        template = Template("{% load votainteligente_extras %}{% if user|is_candidate %}Si{% else %}No{% endif %}")
        context = Context({'user': self.feli})
        self.assertEqual(template.render(context), u'No')
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        self.assertEqual(template.render(context), u'Si')

    def test_get_candidate_home(self):
        url = reverse('backend_candidate:home')
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn(candidacy, response.context['candidacies'])

    def test_get_complete_12_naranja(self):
        election = Election.objects.get(id=2)
        url = reverse('backend_candidate:complete_12_naranja',
                      kwargs={'slug': election.slug,
                              'candidate_id': self.candidate.id})
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
        Candidacy.objects.create(user=self.feli,
                                 candidate=self.candidate
                                 )
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_candidate/complete_12_naranja.html')
        form = response.context['form']

        media_naranja_form_class = get_form_for_election(election)
        self.assertEquals(form.__class__.__name__, media_naranja_form_class.__name__)
        self.assertEquals(form.election, election)
        self.assertEquals(response.context['election'], election)
        self.assertEquals(response.context['candidate'], self.candidate)

    def test_post_complete_12_naranja(self):
        TakenPosition.objects.filter(person=self.candidate).delete()
        election = Election.objects.get(id=2)
        url = reverse('backend_candidate:complete_12_naranja',
                      kwargs={'slug': election.slug,
                              'candidate_id': self.candidate.id})
        self.client.login(username=self.feli,
                          password='alvarez')
        Candidacy.objects.create(user=self.feli,
                                 candidate=self.candidate
                                 )
        data = self.get_form_data_for_area(self.tarapaca)
        response = self.client.post(url, data=data)
        self.assertTrue(TakenPosition.objects.filter(person=self.candidate))
        self.assertRedirects(response, reverse('backend_candidate:home'))


class CandidacyContacts(CandidacyTestCaseBase):
    def setUp(self):
        super(CandidacyContacts, self).setUp()
        self.candidacy = Candidacy.objects.create(user=self.feli,
                                                  candidate=self.candidate
                                                  )

    def test_instanciate(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        self.assertEquals(contact.times_email_has_been_sent, 0)
        self.assertFalse(contact.used_by_candidate)
        self.assertTrue(contact.identifier)
        self.assertEquals(len(contact.identifier.hex), 32)
        self.assertFalse(contact.initial_password)

    def test_candidacy_redirect_view(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        url_kwargs = {'identifier': contact.identifier.hex}
        url = reverse('backend_candidate:candidacy_user_join', kwargs=url_kwargs)

        response = self.client.get(url)
        login_url = reverse('auth_login') + "?next=" + url
        self.assertRedirects(response, login_url)
        self.client.login(username=self.feli.username, password='alvarez')
        response = self.client.get(url)
        candidate_home = reverse('backend_candidate:home')
        self.assertRedirects(response, candidate_home)
        self.assertTrue(Candidacy.objects.filter(candidate=self.candidate,
                                                 user=self.feli))
        candidacy = Candidacy.objects.get(candidate=self.candidate,
                                          user=self.feli)
        contact = CandidacyContact.objects.get(id=contact.id)

        self.assertEquals(contact.candidacy, candidacy)
        self.assertTrue(contact.used_by_candidate)
        self.assertTrue(contact.get_absolute_url().endswith(url))

    def test_contact_sending_email(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        contact.send_mail_with_link()
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertEquals(the_mail.to, [contact.mail])
        url_kwargs = {'identifier': contact.identifier.hex}
        url = reverse('backend_candidate:candidacy_user_join',
                      kwargs=url_kwargs)
        self.assertIn(url, the_mail.body)
        contact = CandidacyContact.objects.get(id=contact.id)
        self.assertEquals(contact.times_email_has_been_sent, 1)

    def test_candidate_sending_email(self):
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@perrito.cl')
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@perrito.cl')
        send_candidate_a_candidacy_link(self.candidate)
        self.assertEquals(len(mail.outbox), 2)

    @override_settings(NOTIFY_CANDIDATES=False)
    def test_not_sending_any_email(self):
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@perrito.cl')
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@perrito.cl')
        send_candidate_a_candidacy_link(self.candidate)
        self.assertEquals(len(mail.outbox), 0)

    @override_settings(MAX_AMOUNT_OF_MAILS_TO_CANDIDATE=3)
    def test_send_candidate_maximum_amount_of_times(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl',
                                                  times_email_has_been_sent=3)

        contact.send_mail_with_link()
        self.assertEquals(len(mail.outbox), 0)

    def test_do_not_send_email_to_candidate_who_is_with_us(self):
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@perrito.cl',
                                        used_by_candidate=True)
        send_candidate_a_candidacy_link(self.candidate)
        self.assertEquals(len(mail.outbox), 0)

    def test_send_mails_to_candidates_tasks(self):
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@perrito.cl')
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@gatito.cl')
        let_candidate_now_about_us.delay()
        self.assertEquals(len(mail.outbox), 2)

    def test_get_url_candidate_login(self):
        url = reverse('backend_candidate:candidate_auth_login')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AuthenticationForm)
        self.assertTemplateUsed(response, 'backend_candidate/auth_login.html')


class SendNewUserToCandidate(CandidacyTestCaseBase):
    def setUp(self):
        super(SendNewUserToCandidate, self).setUp()

    def test_send_mail_with_user_and_password(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        contact.send_mail_with_user_and_password()
        self.assertEquals(contact.times_email_has_been_sent, 1)
        initial_password = contact.initial_password
        self.assertTrue(initial_password)
        user = User.objects.get(username__contains=self.candidate.id)
        contact = CandidacyContact.objects.get(id=contact.id)
        candidacy = contact.candidacy
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(candidacy.candidate, self.candidate)
        self.assertEquals(candidacy.user, user)
        the_mail = mail.outbox[0]
        self.assertEquals(the_mail.to, [contact.mail])
        self.assertIn(user.username, the_mail.body)
        self.assertIn(initial_password, the_mail.body)
        self.assertIn(user.username, the_mail.body)
        site = Site.objects.get_current()
        login_url = reverse('backend_candidate:candidate_auth_login')
        full_login_url = "http://%s%s" % (site.domain, login_url)
        self.assertIn(full_login_url, the_mail.body)
        # It doesn't create user again
        contact.send_mail_with_user_and_password()
        self.assertEquals(len(User.objects.filter(username__contains=self.candidate.id)), 1)
        self.assertEquals(len(mail.outbox), 2)

    def test_login_candidate_marks_her_him_as_contacted(self):
        change_password_url = reverse('password_reset')
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        contact.send_mail_with_user_and_password()
        user = User.objects.get(username__contains=self.candidate.id)
        logged_in = self.client.login(username=user.username,
                                      password=contact.initial_password)
        self.assertTrue(logged_in)
        home_url = reverse('backend_candidate:home')
        response = self.client.get(home_url)
        self.assertRedirects(response, change_password_url)

        response = self.client.get(home_url)
        self.assertEquals(response.status_code, 200)

    @override_settings(MAX_AMOUNT_OF_MAILS_TO_CANDIDATE=3)
    def test_send_candidate_maximum_amount_of_times(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl',
                                                  times_email_has_been_sent=3)

        contact.send_mail_with_user_and_password()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_candidate_their_username_and_password(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        send_candidate_username_and_password(self.candidate)
        contact = CandidacyContact.objects.get(id=contact.id)
        self.assertEquals(contact.times_email_has_been_sent, 1)
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(contact.initial_password, the_mail.body)

    @override_settings(NOTIFY_CANDIDATES=False)
    def test_not_send_candidate_their_username_and_password(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        send_candidate_username_and_password(self.candidate)
        self.assertEquals(len(mail.outbox), 0)

    def test_dont_send_mails_to_candidates_if_they_have_been_contacted(self):
        CandidacyContact.objects.create(candidate=self.candidate,
                                        used_by_candidate=True,
                                        mail='mail@perrito.cl')
        send_candidate_username_and_password(self.candidate)
        self.assertEquals(len(mail.outbox), 0)

    def test_send_mail_management_command(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        call_command('send_user_and_password_to_candidates')
        contact = CandidacyContact.objects.get(id=contact.id)
        self.assertEquals(contact.times_email_has_been_sent, 1)
        the_mail = mail.outbox[0]
        self.assertIn(contact.initial_password, the_mail.body)

    def test_send_mail_task(self):
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@perrito.cl')
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@gatito.cl')
        send_candidates_their_username_and_password.delay()
        self.assertEquals(len(mail.outbox), 2)