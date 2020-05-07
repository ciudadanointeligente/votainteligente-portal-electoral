# coding=utf-8
from backend_candidate.tests import SoulMateCandidateAnswerTestsBase
from elections.models import Candidate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from backend_candidate.models import (Candidacy,
                                      is_candidate,
                                      CandidacyContact,
                                      send_candidate_a_candidacy_link,
                                      add_contact_and_send_mail,
                                      unite_with_candidate_if_corresponds,
                                      send_candidate_username_and_password)
from backend_candidate.forms import get_form_for_election
from backend_candidate.tasks import (let_candidate_now_about_us,
                                     send_candidate_username_and_pasword_task,
                                     send_candidates_their_username_and_password)
from django.template import Template, Context
from elections.models import Election, Area
from candidator.models import TakenPosition
from django.core import mail
from django.test import override_settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site
from django.core.management import call_command
from popular_proposal.models import (Commitment,
                                     PopularProposal,
                                     )


class CandidacyTestCaseBase(SoulMateCandidateAnswerTestsBase):
    def setUp(self):
        super(CandidacyTestCaseBase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password('alvarez')
        self.feli.save()
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password('feroz')
        self.fiera.save()

        self.candidate = Candidate.objects.get(pk=1)
        self.data = {
            'clasification': 'educacion',
            'title': u'Fiera a Santiago',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos\
 y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'causes': u'La super distancia',
            'terms_and_conditions': True
        }
        self.proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       area=self.candidate.election.area,
                                                       data=self.data,
                                                       title=u'This is a title1'
                                                       )
        self.proposal2 = PopularProposal.objects.create(proposer=self.fiera,
                                                        area=self.candidate.election.area,
                                                        data=self.data,
                                                        title=u'This is a title2'
                                                        )


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

    def test_candidate_is_with_us(self):
        candidate = Candidate.objects.get(id=1)
        user = User.objects.create_user(username='user', password='password')
        Candidacy.objects.create(user=user, candidate=candidate)
        self.assertFalse(candidate.has_joined())
        self.client.login(username=user.username, password='password')
        user = User.objects.get(id=user.id)
        self.assertTrue(user.last_login)
        self.assertTrue(candidate.has_joined())

    def test_candidacy_has_logged_in(self):
        user = User.objects.create_user(username='user', password='password')
        candidacy = Candidacy.objects.create(user=user,
                                             candidate=self.candidate
                                             )
        self.assertFalse(self.candidate.has_logged_in())
        self.client.login(username='user', password='password')
        url = reverse('backend_candidate:home')
        self.client.get(url)

        self.assertTrue(self.candidate.has_logged_in())

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
        Candidacy.objects.create(user=self.feli,
                                 candidate=self.candidate
                                 )

        response = self.client.get(url)
        profile_url = reverse('backend_candidate:complete_profile',
                              kwargs={'slug': self.candidate.election.slug,
                                      'candidate_slug': self.candidate.slug})
        self.assertRedirects(response, profile_url)

    def test_proposals_with_a_resolution(self):

        Candidacy.objects.create(user=self.feli,
                                 candidate=self.candidate
                                 )
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.proposal,
                                               commited=True)

        candidate2 = Candidate.objects.get(id=2)
        commitment2 = Commitment.objects.create(candidate=candidate2,
                                                proposal=self.proposal,
                                                commited=True)

        election = self.candidate.election
        url = reverse('backend_candidate:my_proposals_with_a_resolution',
                      kwargs={'slug': election.slug,
                              'candidate_slug': self.candidate.slug})
        login_url = reverse('auth_login') + "?next=" + url
        response = self.client.get(url)
        self.assertRedirects(response, login_url)
        self.client.login(username=self.fiera,
                          password='feroz')

        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_candidate/i_have_commited.html')
        self.assertIn(commitment, response.context['commitments'])
        self.assertNotIn(commitment2, response.context['commitments'])
        self.assertEquals(self.candidate, response.context['candidate'])
        self.assertEquals(self.candidate.election, response.context['election'])

    def test_proposals_for_me(self):
        Candidacy.objects.create(user=self.feli,
                                 candidate=self.candidate
                                 )
        election = self.candidate.election
        election.candidates_can_commit_everywhere = False
        election.save()
        # Proposal1 doesn't have a commitment so it should be in the lis
        # Proposal for another area
        another_area = Area.objects.create(name='another area')
        proposal3 = PopularProposal.objects.create(proposer=self.fiera,
                                                   area=another_area,
                                                   data=self.data,
                                                   title=u'This is a title2'
                                                   )
        Commitment.objects.create(candidate=self.candidate,
                                  proposal=self.proposal2,
                                  commited=True)

        url = reverse('backend_candidate:proposals_for_me',
                      kwargs={'slug': self.candidate.election.slug,
                              'candidate_slug': self.candidate.slug})

        login_url = reverse('auth_login') + "?next=" + url
        response = self.client.get(url)
        self.assertRedirects(response, login_url)
        self.client.login(username=self.fiera,
                          password='feroz')

        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_candidate/proposals_for_me.html')
        self.assertIn(self.proposal, response.context['proposals'])
        # Should not be here since it has a commitment
        self.assertNotIn(self.proposal2, response.context['proposals'])
        # Should not be here since it was made for another area
        self.assertNotIn(proposal3, response.context['proposals'])
        self.assertEquals(self.candidate, response.context['candidate'])
        self.assertEquals(self.candidate.election, response.context['election'])

    def test_proposals_for_me_when_election_can_accept_from_everywhere(self):
        Candidacy.objects.create(user=self.feli,
                                 candidate=self.candidate
                                 )
        election = self.candidate.election
        election.candidates_can_commit_everywhere = True
        election.save()
        # Proposal1 doesn't have a commitment so it should be in the lis
        # Proposal for another area
        another_area = Area.objects.create(name='another area')
        Commitment.objects.create(candidate=self.candidate,
                                  proposal=self.proposal2,
                                  commited=True)
        proposal3 = PopularProposal.objects.create(proposer=self.fiera,
                                                   area=another_area,
                                                   data=self.data,
                                                   title=u'This is a title2'
                                                   )
        url = reverse('backend_candidate:proposals_for_me',
                      kwargs={'slug': self.candidate.election.slug,
                              'candidate_slug': self.candidate.slug})
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertIn(self.proposal, response.context['proposals'])
        # Should not be here since it has a commitment
        self.assertNotIn(self.proposal2, response.context['proposals'])
        # Should totaly be here since it was made for another area, but my election allows me to commit everywhere
        self.assertIn(proposal3, response.context['proposals'])

    def test_get_complete_12_naranja(self):
        election = Election.objects.get(id=2)
        url = reverse('backend_candidate:complete_12_naranja',
                      kwargs={'slug': election.slug,
                              'candidate_slug': self.candidate.slug})
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
                              'candidate_slug': self.candidate.slug})
        self.client.login(username=self.feli,
                          password='alvarez')
        Candidacy.objects.create(user=self.feli,
                                 candidate=self.candidate
                                 )
        data = self.get_form_data_for_area(self.tarapaca)
        response = self.client.post(url, data=data)
        self.assertTrue(TakenPosition.objects.filter(person=self.candidate))
        self.assertRedirects(response, url)

    def test_candidacy_get_complete_profile_url(self):
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                              )
        url = reverse('backend_candidate:complete_profile',
                              kwargs={'slug': self.candidate.election.slug,
                              'candidate_slug': self.candidate.slug})
        self.assertEquals(candidacy.get_complete_profile_url(), url)


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

    def test_create_and_set_user(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        contact.create_and_set_user()
        contact.refresh_from_db()
        self.assertTrue(contact.candidacy)
        self.assertTrue(contact.user)

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
        candidacy = Candidacy.objects.get(candidate=self.candidate,
                                          user=self.feli)
        profile_url = reverse('backend_candidate:complete_profile',
                              kwargs={'slug': candidacy.candidate.election.slug,
                                      'candidate_slug': candidacy.candidate.slug})
        self.assertRedirects(response, profile_url)
        self.assertTrue(Candidacy.objects.filter(candidate=self.candidate,
                                                 user=self.feli))
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

class UnifyCandidateAndUserWhenTheyHaveTheSamePassword(CandidacyTestCaseBase):
    def setUp(self):
        super(UnifyCandidateAndUserWhenTheyHaveTheSamePassword, self).setUp()

    def test_users_with_mail_in_candidates_unify(self):
        email = 'candidate@party.com'
        user_that_is_also_candidate = User.objects.create_user(username='Name',
                                                               password='password',
                                                               email=email)
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail=email)
        unite_with_candidate_if_corresponds(user_that_is_also_candidate)
        self.assertTrue(Candidacy.objects.filter(user=user_that_is_also_candidate, candidate=self.candidate))

    def test_does_not_create_two_candidacies(self):
        email = 'candidate@party.com'
        user_that_is_also_candidate = User.objects.create_user(username='Name',
                                                               password='password',
                                                               email=email)
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail=email)
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail=email)
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail=email)
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail=email)
        unite_with_candidate_if_corresponds(user_that_is_also_candidate)
        self.assertEquals(Candidacy.objects.filter(user=user_that_is_also_candidate, candidate=self.candidate).count(), 1)

    def test_what_if_users_has_an_emtpy_email(self):
        email = 'candidate@party.com'
        user_that_is_also_candidate = User.objects.create_user(username='Name',
                                                               password='password',
                                                               email=None)
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail=email)
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail=email)
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail=email)
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail=email)
        self.assertFalse(Candidacy.objects.filter(user=user_that_is_also_candidate, candidate=self.candidate).count())

        user_that_is_also_candidate = User.objects.create_user(username='Name1',
                                                               password='password',
                                                               email='')
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='')
        self.assertFalse(Candidacy.objects.filter(user=user_that_is_also_candidate, candidate=self.candidate).count())
        user_that_is_also_candidate = User.objects.create_user(username='Name2',
                                                               password='password',
                                                               email=None)
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='')
        self.assertFalse(Candidacy.objects.filter(user=user_that_is_also_candidate, candidate=self.candidate).count())

    def test_unify_at_creation(self):
        email = 'candidate@party.com'

        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail=email)
        user_that_is_also_candidate = User.objects.create_user(username='Name',
                                                               password='password',
                                                               email=email)
        self.assertEquals(Candidacy.objects.filter(user=user_that_is_also_candidate, candidate=self.candidate).count(), 1)


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
        user = User.objects.get(username__contains=self.candidate.slug)
        self.assertEquals(user.email, contact.mail)
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
        # self.assertIn(full_login_url, the_mail.body)
        # It doesn't create user again
        contact.send_mail_with_user_and_password()
        self.assertEquals(len(User.objects.filter(username__contains=self.candidate.slug)), 1)
        self.assertEquals(len(mail.outbox), 2)

    def test_login_candidate_marks_her_him_as_contacted(self):
        change_password_url = reverse('password_reset')
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        contact.send_mail_with_user_and_password()
        user = User.objects.get(username__contains=self.candidate.slug)
        logged_in = self.client.login(username=user.username,
                                      password=contact.initial_password)
        self.assertTrue(logged_in)
        home_url = reverse('backend_candidate:home')
        response = self.client.get(home_url)
        self.assertRedirects(response, change_password_url)

        response = self.client.get(home_url)
        profile_url = reverse('backend_candidate:complete_profile',
                              kwargs={'slug': contact.candidacy.candidate.election.slug,
                                      'candidate_slug': contact.candidacy.candidate.slug})
        self.assertRedirects(response, profile_url)

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

    def test_send_candidate_username_and_password_task(self):
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        result = send_candidate_username_and_pasword_task.delay(self.candidate)
        contact = CandidacyContact.objects.get(id=contact.id)
        self.assertEquals(contact.times_email_has_been_sent, 1)
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(contact.initial_password, the_mail.body)

    def test_add_contact_and_send_mail(self):
        add_contact_and_send_mail('mail.perrito@fiera.cl', self.candidate)
        contact = CandidacyContact.objects.get(mail='mail.perrito@fiera.cl', candidate=self.candidate)
        self.assertTrue(contact)
        contact = CandidacyContact.objects.get(id=contact.id)
        self.assertEquals(contact.times_email_has_been_sent, 1)
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(contact.initial_password, the_mail.body)

    def test_add_contact_and_send_mail_command(self):
        call_command('add_contact_and_send_mail', 'mail.perrito@fiera.cl', self.candidate.slug)
        contact = CandidacyContact.objects.get(mail='mail.perrito@fiera.cl', candidate=self.candidate)
        self.assertTrue(contact)
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

    def test_send_mail_area_management_command(self):
        a = Area.objects.create(name='Area')
        e = Election.objects.create(name=u'Election', area=a)
        other_candidate2 = Candidate.objects.create(name='Nombre')
        e.candidates.add(other_candidate2)
        self.assertNotEqual(other_candidate2.election.area,
                            self.candidate.election.area)
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl')
        contact2 = CandidacyContact.objects.create(candidate=other_candidate2,
                                                   mail='mail@gatito.cl')
        area_id = self.candidate.election.area.id
        call_command('send_user_and_password_to_candidates_from', area_id)
        contact = CandidacyContact.objects.get(id=contact.id)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(contact.times_email_has_been_sent, 1)
        the_mail = mail.outbox[0]
        self.assertIn(contact.initial_password, the_mail.body)
        self.assertNotIn(contact2.mail, the_mail.to)

    def test_send_mail_task(self):
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@perrito.cl')
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@gatito.cl')
        send_candidates_their_username_and_password.delay()
        self.assertEquals(len(mail.outbox), 2)
