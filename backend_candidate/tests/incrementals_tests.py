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
