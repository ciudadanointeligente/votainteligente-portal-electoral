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
                                      send_candidate_username_and_password)
from suggestions_for_candidates.models import (IncrementalsCandidateFilter,
                                               ProposalSuggestionForIncremental,
                                               CandidateIncremental)
from backend_candidate.forms import (get_form_for_election,)
from suggestions_for_candidates.forms import (SimpleCommitmentForm,
                                              get_multi_commitment_forms)
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
from django.core.management import call_command
from django.forms import Form
from django.core.urlresolvers import reverse
from suggestions_for_candidates.tasks import send_suggestions_tasks


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
        self.assertFalse(f.subject)
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
                                                                     summary=u"Por esta razón",
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
        e = Election.objects.first()
        damian_candidato = Candidate.objects.create(name='Jefe!')
        damian_candidato.elections.add(e)
        d_1 = User.objects.create(username='d1', email='damian1@perrito.cl')
        d_2 = User.objects.create(username='d2', email='damian2@perrito.cl')
        Candidacy.objects.create(candidate=damian_candidato, user=d_1)
        Candidacy.objects.create(candidate=damian_candidato, user=d_2)
        PersonalData.objects.create(candidate=damian_candidato, label='Pacto', value="Frente Amplio")

        fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!')
        fiera_candidata.elections.add(e)
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
                                                       text=u"te querimos musho\n\rsaltode linea",
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

    def test_command_line(self):
        e = Election.objects.first()
        damian_candidato = Candidate.objects.create(name='Jefe!')
        damian_candidato.elections.add(e)
        d_1 = User.objects.create(username='d1', email='damian1@perrito.cl')
        d_2 = User.objects.create(username='d2', email='damian2@perrito.cl')
        Candidacy.objects.create(candidate=damian_candidato, user=d_1)
        Candidacy.objects.create(candidate=damian_candidato, user=d_2)
        PersonalData.objects.create(candidate=damian_candidato, label='Pacto', value="Frente Amplio")

        fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!')
        fiera_candidata.elections.add(e)
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
                                                       subject="Esto es un custom subject",
                                                       text=u"te querimos musho\n\rsaltode linea",
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

        call_command("send_all_filters_to_candidates")
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 4)
        first_email = mail.outbox[original_amount_of_mails]
        possible_emails_that_could_have_been_used = [d_1.email,
                                                     d_2.email,
                                                     f_1.email,
                                                     f_2.email]
        self.assertIn(first_email.to[0], possible_emails_that_could_have_been_used)
        self.assertEquals(first_email.subject, f.subject)

    def test_command_line_for_selected_filters(self):
        e = Election.objects.first()
        damian_candidato = Candidate.objects.create(name='Jefe!', slug="jefe")
        damian_candidato.elections.add(e)
        d_1 = User.objects.create(username='d1', email='damian1@perrito.cl')
        d_2 = User.objects.create(username='d2', email='damian2@perrito.cl')
        Candidacy.objects.create(candidate=damian_candidato, user=d_1)
        Candidacy.objects.create(candidate=damian_candidato, user=d_2)
        PersonalData.objects.create(candidate=damian_candidato, label='Pacto', value="Frente Amplio")

        fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!')
        fiera_candidata.elections.add(e)
        PersonalData.objects.create(candidate=fiera_candidata, label='Pacto', value="Frente Amplio")
        f_1 = User.objects.create(username='f1', email='mail1@perrito.cl')
        f_2 = User.objects.create(username='f2', email='mail2@perrito.cl')
        Candidacy.objects.create(candidate=fiera_candidata, user=f_1)
        Candidacy.objects.create(candidate=fiera_candidata, user=f_2)

        benito_candidato = Candidate.objects.create(name='Beni el mejor del mundo!', slug="beni")
        beni_1 = User.objects.create(username='beni', email='beni@perrito.cl')
        Candidacy.objects.create(candidate=benito_candidato, user=beni_1)
        PersonalData.objects.create(candidate=benito_candidato, label='Pacto', value="Otro Pacto")
        filter_qs2 = {'slug':'beni'}
        exclude_qs2 = {}
        f2 = IncrementalsCandidateFilter.objects.create(filter_qs=filter_qs2,
                                                       exclude_qs=exclude_qs2,
                                                       name=u"Candidatos benitos")

        filter_qs = {'personal_datas__label': "Pacto", "personal_datas__value": u"Frente Amplio"}
        exclude_qs = {'elections__position': "Presidenta o Presidente"}
        f = IncrementalsCandidateFilter.objects.create(filter_qs=filter_qs,
                                                       exclude_qs=exclude_qs,
                                                       text=u"te querimos musho\n\rsaltode linea",
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
        ProposalSuggestionForIncremental.objects.create(incremental=f2,
                                                        proposal=p1)
        ProposalSuggestionForIncremental.objects.create(incremental=f2,
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

        call_command("send_selected_filters_to_candidates", str(f2.id))
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 1)
        first_email = mail.outbox[original_amount_of_mails]
        possible_emails_that_could_have_been_used = [beni_1.email]
        for mail_index in range(original_amount_of_mails, original_amount_of_mails + 1):
            m = mail.outbox[mail_index]
            self.assertIn(m.to[0], possible_emails_that_could_have_been_used)

    def test_task_for_sending_suggestions(self):
        e = Election.objects.first()
        damian_candidato = Candidate.objects.create(name='Jefe!', slug="jefe")
        damian_candidato.elections.add(e)
        d_1 = User.objects.create(username='d1', email='damian1@perrito.cl')
        d_2 = User.objects.create(username='d2', email='damian2@perrito.cl')
        Candidacy.objects.create(candidate=damian_candidato, user=d_1)
        Candidacy.objects.create(candidate=damian_candidato, user=d_2)
        PersonalData.objects.create(candidate=damian_candidato, label='Pacto', value="Frente Amplio")

        fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!')
        fiera_candidata.elections.add(e)
        PersonalData.objects.create(candidate=fiera_candidata, label='Pacto', value="Frente Amplio")
        f_1 = User.objects.create(username='f1', email='mail1@perrito.cl')
        f_2 = User.objects.create(username='f2', email='mail2@perrito.cl')
        Candidacy.objects.create(candidate=fiera_candidata, user=f_1)
        Candidacy.objects.create(candidate=fiera_candidata, user=f_2)

        benito_candidato = Candidate.objects.create(name='Beni el mejor del mundo!', slug="beni")
        beni_1 = User.objects.create(username='beni', email='beni@perrito.cl')
        Candidacy.objects.create(candidate=benito_candidato, user=beni_1)
        PersonalData.objects.create(candidate=benito_candidato, label='Pacto', value="Otro Pacto")
        filter_qs2 = {'slug':'beni'}
        exclude_qs2 = {}
        f2 = IncrementalsCandidateFilter.objects.create(filter_qs=filter_qs2,
                                                       exclude_qs=exclude_qs2,
                                                       name=u"Candidatos benitos")

        filter_qs = {'personal_datas__label': "Pacto", "personal_datas__value": u"Frente Amplio"}
        exclude_qs = {'elections__position': "Presidenta o Presidente"}
        f = IncrementalsCandidateFilter.objects.create(filter_qs=filter_qs,
                                                       exclude_qs=exclude_qs,
                                                       text=u"te querimos musho\n\rsaltode linea",
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
        ProposalSuggestionForIncremental.objects.create(incremental=f2,
                                                        proposal=p1)
        ProposalSuggestionForIncremental.objects.create(incremental=f2,
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
        send_suggestions_tasks.delay(f2)
        stafs = User.objects.filter(is_staff=True)
        stafs_emails = [u.email for u in stafs]
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 3)
        first_email = mail.outbox[original_amount_of_mails]
        possible_emails_that_could_have_been_used = [beni_1.email] + stafs_emails
        for mail_index in range(original_amount_of_mails, original_amount_of_mails + 1):
            m = mail.outbox[mail_index]
            self.assertIn(m.to[0], possible_emails_that_could_have_been_used)


class CandidateIncrementalIdentifier(ProposingCycleTestCaseBase):
    def setUp(self):
        super(CandidateIncrementalIdentifier, self).setUp()
        self.fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!')
        e = Election.objects.first()
        e.candidates.add(self.fiera_candidata)
        PersonalData.objects.create(candidate=self.fiera_candidata, label='Pacto', value="Frente Amplio")
        filter_qs = {'personal_datas__label': "Pacto", "personal_datas__value": u"Frente Amplio"}
        exclude_qs = {'elections__position': "Presidenta o Presidente"}
        self.filter = IncrementalsCandidateFilter.objects.create(filter_qs=filter_qs,
                                                                 exclude_qs=exclude_qs,
                                                                 text=u"te querimos musho\n\rsaltode linea",
                                                                 name=u"Candidatos al parlamento de Frente Amplio")
        self.p1 = PopularProposal.objects.create(proposer=self.feli,
                                                 area=self.arica,
                                                 data=self.data,
                                                 title=u'This is a title1'
                                                 )
        self.p2 = PopularProposal.objects.create(proposer=self.feli,
                                                 area=self.arica,
                                                 data=self.data,
                                                 title=u'This is a title1'
                                                 )
        ProposalSuggestionForIncremental.objects.create(incremental=self.filter,
                                                        proposal=self.p1)
        ProposalSuggestionForIncremental.objects.create(incremental=self.filter,
                                                        proposal=self.p2)

    def test_candidate_incremental_model(self):
        candidate_incremental = CandidateIncremental.objects.create(candidate=self.fiera_candidata,
                                                                    suggestion=self.filter)
        self.assertTrue(candidate_incremental.identifier)
        self.assertFalse(candidate_incremental.used)

    def test_candidate_incremental_autocreatel(self):
        self.filter.send_mails()
        c_i = CandidateIncremental.objects.get(suggestion=self.filter, candidate=self.fiera_candidata)
        self.filter.send_mails()
        cis = CandidateIncremental.objects.filter(suggestion=self.filter, candidate=self.fiera_candidata)
        self.assertEquals(cis.count(), 2)

    def test_candidate_incremental_formset(self):
        self.filter.send_mails()
        c_i = CandidateIncremental.objects.get(suggestion=self.filter, candidate=self.fiera_candidata)
        self.assertEquals(len(c_i.formset.forms), 2)
        self.assertEquals(c_i.formset.forms[0].candidate, self.fiera_candidata)
        self.assertEquals(c_i.formset.forms[1].candidate, self.fiera_candidata)
        self.assertEquals(c_i.formset.forms[0].proposal, self.p1)
        self.assertEquals(c_i.formset.forms[1].proposal, self.p2)


    def test_reverse_self(self):
        c_i = CandidateIncremental.objects.create(candidate=self.fiera_candidata,
                                                  suggestion=self.filter)
        url = reverse("suggestions_for_candidates:commit_to_suggestions", kwargs={"identifier": c_i.identifier})
        self.assertEquals(c_i.get_absolute_url(), url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('formset', response.context)
        formset = response.context['formset']
        self.assertEquals(len(formset.forms), 2)
        self.assertEquals(formset.forms[0].candidate, self.fiera_candidata)
        self.assertEquals(formset.forms[1].candidate, self.fiera_candidata)
        self.assertEquals(formset.forms[0].proposal, self.p1)
        self.assertEquals(formset.forms[1].proposal, self.p2)

    def test_post_to_commit(self):
        data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MAX_NUM_FORMS': '2',
            'form-0-commited': True,
            'form-0-detail': "me gustan estas propuestas",
            'form-1-commited': False,
            'form-1-detail': "me gustan estas propuestas",

        }

        c_i = CandidateIncremental.objects.create(candidate=self.fiera_candidata,
                                                  suggestion=self.filter)
        url = reverse("suggestions_for_candidates:commit_to_suggestions", kwargs={"identifier": c_i.identifier})
        response = self.client.post(url, data)
        c1 = Commitment.objects.get(candidate=self.fiera_candidata,
                                    proposal=self.p1)
        self.assertFalse(Commitment.objects.filter(candidate=self.fiera_candidata,
                                                   proposal=self.p2))
        self.assertIn(c1, response.context['commitments'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


class MultiCommitmentForm(ProposingCycleTestCaseBase):
    def setUp(self):
        super(MultiCommitmentForm, self).setUp()
        self.feli = User.objects.get(username='feli')

    def test_instanciate_single_form(self):
        fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!')
        e = Election.objects.first()
        e.candidates.add(fiera_candidata)
        proposal = PopularProposal.objects.create(proposer=self.feli,
                                                  area=self.arica,
                                                  data=self.data,
                                                  title=u'This is a title'
                                                  )
        form = SimpleCommitmentForm(candidate=fiera_candidata,
                                    proposal=proposal)
        self.assertIsInstance(form, Form)
        self.assertTrue(form.fields['commited'])
        self.assertTrue(form.fields['detail'])
        data = {'commited': True, 'detail': u"si así funcion"}
        form = SimpleCommitmentForm(data=data,
                                    candidate=fiera_candidata,
                                    proposal=proposal)
        self.assertTrue(form.is_valid())
        commitment = form.save()
        self.assertTrue(commitment.commited)
        self.assertEquals(commitment.candidate, fiera_candidata)
        self.assertEquals(commitment.proposal, proposal)
        #  DONT CREATE TWO COMMITMENTS
        form = SimpleCommitmentForm(data=data,
                                    candidate=fiera_candidata,
                                    proposal=proposal)
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertIsNone(result)
        self.assertEquals(len(Commitment.objects.filter(proposal=proposal)), 1)
        commitment.delete()
        data = {}
        form = SimpleCommitmentForm(data=data,
                                    candidate=fiera_candidata,
                                    proposal=proposal)
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertIsNone(result)
        self.assertFalse(len(Commitment.objects.filter(proposal=proposal)))

    def test_get_formset(self):
        fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!')
        e = Election.objects.first()
        e.candidates.add(fiera_candidata)
        proposal1 = PopularProposal.objects.create(proposer=self.feli,
                                                   area=self.arica,
                                                   data=self.data,
                                                   title=u'This is a title'
                                                   )
        proposal2 = PopularProposal.objects.create(proposer=self.feli,
                                                   area=self.arica,
                                                   data=self.data,
                                                   title=u'This is a title'
                                                   )
        formset = get_multi_commitment_forms(fiera_candidata, [proposal1, proposal2], ['s1', 's2'])()
        self.assertEquals(len(formset.forms), 2)
        self.assertEquals(formset.forms[0].candidate, fiera_candidata)
        self.assertEquals(formset.forms[1].candidate, fiera_candidata)
        self.assertEquals(formset.forms[0].proposal, proposal1)
        self.assertEquals(formset.forms[1].proposal, proposal2)
        self.assertEquals(formset.forms[0].summary, 's1')
        self.assertEquals(formset.forms[1].summary, 's2')

    # def test_commitment_view(self):
    #     url = reverse('proposal_subscriptions:unsubscribe', kwargs={'token': subscription.token})
