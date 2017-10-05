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
from popolo.models import ContactDetail


class HelpFindingCandidatesTestCase(SoulMateCandidateAnswerTestsBase):
    def setUp(self):
        super(HelpFindingCandidatesTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.candidate1 = Candidate.objects.get(pk=1)
        self.candidate2 = Candidate.objects.get(pk=2)
        self.candidate3 = Candidate.objects.get(pk=3)
        self.candidate4 = Candidate.objects.get(pk=4)
        self.candidate5 = Candidate.objects.get(pk=5)
        self.candidate6 = Candidate.objects.get(pk=6)

    def test_page_listing_candidates(self):
        url = reverse('help')
        self.assertEquals(self.client.get(url).status_code, 200)

        Candidacy.objects.create(user=self.feli,
                                 candidate=self.candidate1
                                 )
        self.client.login(username=self.feli,
                          password='alvarez')

        # Should not be in because has user that has logged in and has completed 1/2 naranja
        response = self.client.get(url)
        self.assertNotIn(self.candidate1, response.context['candidates'])
        # Should be here because we hace a contact detail and hasn't log in
        self.feli.last_login = None
        self.feli.save()
        Candidacy.objects.create(user=self.feli,
                                 candidate=self.candidate2)
        self.candidate2.taken_positions.all().delete()
        self.candidate2.add_contact_detail(contact_type='TWITTER', value='perrito', label='perrito')
        response = self.client.get(url)
        self.assertIn(self.candidate2, response.context['candidates'])
        # candidate 3 is not here because even though hasn't log in and doesn't have answers,
        # we dont have a way to contact her/him
        self.feli.last_login = None
        self.feli.save()
        Candidacy.objects.create(user=self.feli,
                                 candidate=self.candidate3)
        self.candidate3.taken_positions.all().delete()
        self.candidate3.add_contact_detail(contact_type='TWITTER', value='perrito', label='perrito')
        response = self.client.get(url)
        self.assertIn(self.candidate3, response.context['candidates'])
