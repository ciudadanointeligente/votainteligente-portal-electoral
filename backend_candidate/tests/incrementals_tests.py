# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from elections.models import Candidate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from backend_candidate.models import (Candidacy,
                                      is_candidate,
                                      CandidacyContact,
                                      send_candidate_a_candidacy_link,
                                      add_contact_and_send_mail,
                                      IncrementalsCandidateFilter,
                                      ProposalSuggestionForIncremental,
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
from elections.models import PersonalData


class IncrementalsTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(IncrementalsTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')

    def test_instanciate_a_filter_for_incrementals(self):
        #  Candidate.objects.filter(personal_datas__label="Pacto", personal_datas__value=u"Frente Amplio")
        filter_qs = {'personal_datas__label': "Pacto", "personal_datas__value": u"Frente Amplio"}
        exclude_qs = {'elections__position': "Presidenta o Presidente"}
        f = IncrementalsCandidateFilter.objects.create(filter_qs=filter_qs,
                                                       exclude_qs=exclude_qs,
                                                       name=u"Candidatos al parlamento de Frente Amplio",
                                                       text=u"Este texto cambia en base al envío")
        self.assertTrue(f)

    def test_instanciate_suggestion_to_incremental_filter(self):
        filter_qs = {'personal_datas__label': "Pacto", "personal_datas__value": u"Frente Amplio"}
        exclude_qs = {'elections__position': "Presidenta o Presidente"}
        f = IncrementalsCandidateFilter.objects.create(filter_qs=filter_qs,
                                                       exclude_qs=exclude_qs,
                                                       name=u"Candidatos al parlamento de Frente Amplio")
        proposal = PopularProposal.objects.create(proposer=self.feli,
                                                  area=self.arica,
                                                  data=self.data,
                                                  title=u'This is a title'
                                                  )
        suggestion = ProposalSuggestionForIncremental.objects.create(incremental=f,
                                                                     proposal=proposal)
        self.assertFalse(suggestion.sent)

    def test_filter_with_proposals(self):
        p1 = PopularProposal.objects.create(proposer=self.feli,
                                            area=self.arica,
                                            data=self.data,
                                            title=u'This is a title1'
                                            )
        p2 = PopularProposal.objects.create(proposer=self.feli,
                                            area=self.arica,
                                            data=self.data,
                                            title=u'This is a title1'
                                            )
        f = IncrementalsCandidateFilter.objects.create(filter_qs={},
                                                       exclude_qs={},
                                                       name=u"Candidatos al parlamento de Frente Amplio")
        ProposalSuggestionForIncremental.objects.create(incremental=f,
                                                        proposal=p1)
        ProposalSuggestionForIncremental.objects.create(incremental=f,
                                                        proposal=p2)
        self.assertIn(p1, f.suggested_proposals.all())
        self.assertIn(p2, f.suggested_proposals.all())

    def test_filter_candidates(self):
        fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!')
        PersonalData.objects.create(candidate=fiera_candidata, label='Pacto', value="Frente Amplio")
        benito_candidato = Candidate.objects.create(name='Beni el mejor del mundo!')
        PersonalData.objects.create(candidate=benito_candidato, label='Pacto', value="Otro Pacto")

        filter_qs = {'personal_datas__label': "Pacto", "personal_datas__value": u"Frente Amplio"}
        exclude_qs = {'elections__position': "Presidenta o Presidente"}
        f = IncrementalsCandidateFilter.objects.create(filter_qs=filter_qs,
                                                       exclude_qs=exclude_qs,
                                                       name=u"Candidatos al parlamento de Frente Amplio")
        candidates = f.get_candidates()
        self.assertIn(fiera_candidata, candidates)
        self.assertNotIn(benito_candidato, candidates)

    def test_send_mail_per_candidate(self):
        damian_candidato = Candidate.objects.create(name='Jefe!')
        d_1 = User.objects.create(username='d1', email='damian1@perrito.cl')
        d_2 = User.objects.create(username='d2', email='damian2@perrito.cl')
        Candidacy.objects.create(candidate=damian_candidato, user=d_1)
        Candidacy.objects.create(candidate=damian_candidato, user=d_2)
        PersonalData.objects.create(candidate=damian_candidato, label='Pacto', value="Frente Amplio")

        fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!')
        PersonalData.objects.create(candidate=fiera_candidata, label='Pacto', value="Frente Amplio")
        f_1 = User.objects.create(username='f1', email='mail1@perrito.cl')
        f_2 = User.objects.create(username='f2', email='mail2@perrito.cl')
        Candidacy.objects.create(candidate=fiera_candidata, user=f_1)
        Candidacy.objects.create(candidate=fiera_candidata, user=f_2)

        benito_candidato = Candidate.objects.create(name='Beni el mejor del mundo!')
        PersonalData.objects.create(candidate=benito_candidato, label='Pacto', value="Otro Pacto")
        CandidacyContact.objects.create(candidate=benito_candidato,
                                        mail='mail3@perrito.cl')
        
        CandidacyContact.objects.create(candidate=benito_candidato,
                                        mail='mail4@perrito.cl')

        filter_qs = {'personal_datas__label': "Pacto", "personal_datas__value": u"Frente Amplio"}
        exclude_qs = {'elections__position': "Presidenta o Presidente"}
        f = IncrementalsCandidateFilter.objects.create(filter_qs=filter_qs,
                                                       exclude_qs=exclude_qs,
                                                       text=u"te querimos musho\n\r saltode linea",
                                                       name=u"Candidatos al parlamento de Frente Amplio")
        p1 = PopularProposal.objects.create(proposer=self.feli,
                                            area=self.arica,
                                            data=self.data,
                                            title=u'This is a title1'
                                            )
        p2 = PopularProposal.objects.create(proposer=self.feli,
                                            area=self.arica,
                                            data=self.data,
                                            title=u'This is a title1'
                                            )
        ProposalSuggestionForIncremental.objects.create(incremental=f,
                                                        proposal=p1)
        ProposalSuggestionForIncremental.objects.create(incremental=f,
                                                        proposal=p2)
        context = f.get_mail_context()
        self.assertIn(p1, context['proposals'].all())
        self.assertIn(p2, context['proposals'].all())

        # Jefe comprometido y enamorado
        Commitment.objects.create(candidate=damian_candidato,
                                  proposal=p1,
                                  detail=u'Yo me comprometo',
                                  commited=True)
        propuestas_for_damian = f.get_proposals_for_candidate(damian_candidato)
        self.assertNotIn(p1, propuestas_for_damian)
        self.assertIn(p2, propuestas_for_damian)
        propuestas_for_fiera = f.get_proposals_for_candidate(fiera_candidata)
        self.assertIn(p1, propuestas_for_fiera)
        self.assertIn(p2, propuestas_for_fiera)
        
        context_for_damian = f.get_context_for_candidate(damian_candidato)
        expected_context_for_d = {"candidate": damian_candidato,
                                  "proposals": propuestas_for_damian,
                                  "text": f.text}
        self.assertEquals(context_for_damian, expected_context_for_d)

        original_amount_of_mails = len(mail.outbox)
        f.send_mails()

        self.assertEquals(len(mail.outbox), original_amount_of_mails + 4)
        first_email = mail.outbox[original_amount_of_mails]
        possible_emails_that_could_have_been_used = [d_1.email,
                                                     d_2.email,
                                                     f_1.email,
                                                     f_2.email]
        self.assertIn(first_email.to[0], possible_emails_that_could_have_been_used)

        print first_email.body
        self.fail()
