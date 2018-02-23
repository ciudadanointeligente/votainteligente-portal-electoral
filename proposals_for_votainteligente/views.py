# coding=utf-8
from collections import OrderedDict
from backend_candidate.models import Candidacy

from constance import config

import copy

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.http import HttpResponseNotFound, JsonResponse, HttpResponse, Http404

from django.shortcuts import get_object_or_404

from django.template.response import TemplateResponse

from django.utils.decorators import method_decorator

from django.utils.translation import ugettext as _

from django.views.generic import View

from django.views.generic.detail import DetailView

from django.views.generic.edit import FormView, UpdateView
from django.views.generic.base import RedirectView

from django.views.generic.list import ListView

from django_filters.views import FilterView

from elections.models import Area, Candidate

from django import forms

from proposals_for_votainteligente.filters import (ProposalGeneratedAtFilter)

from popular_proposal.forms import (UpdateProposalForm,
                                    SubscriptionForm,
                                    )

from popular_proposal.models import (Commitment,
                                     PopularProposal,
                                     ProposalLike,
                                     ProposalTemporaryData,)

from votainteligente.view_mixins import EmbeddedViewBase
import random
from django.conf import settings
from popular_proposal.views.proposal_views import (ThanksForProposingViewBase,
                                                   CommitViewBase,
                                                   NotCommitViewBase,
                                                   ProposalFilterMixin,)
from popular_proposal.views.wizard import (ProposalWizardBase)
from proposals_for_votainteligente.forms import (ProposalWithAreaForm,
                                                 VotaInteligenteAuthorityCommitmentForm,
                                                 VotaInteligenteAuthorityNotCommitingForm)
from popular_proposal import wizard_previous_form_classes
from popular_proposal.forms import (get_form_list,)

class WithinAreaProposalCreationView(FormView):
    template_name = 'popular_proposal/create.html'
    form_class = ProposalWithAreaForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, id=self.kwargs['slug'])
        return super(WithinAreaProposalCreationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(WithinAreaProposalCreationView, self).get_context_data(**kwargs)
        kwargs['area'] = self.area
        return kwargs

    def get_form_kwargs(self):
        kwargs = super(WithinAreaProposalCreationView, self).get_form_kwargs()
        kwargs['proposer'] = self.request.user
        kwargs['area'] = self.area
        return kwargs

    def form_valid(self, form):
        self.proposal = form.save()
        return super(WithinAreaProposalCreationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('popular_proposals:thanks',
                       kwargs={'pk': self.proposal.id})

class CommitView(CommitViewBase):
    form_class = VotaInteligenteAuthorityCommitmentForm
    def determine_if_authority_can_commit(self):
        self.candidate = get_object_or_404(Candidate,
                                           id=self.kwargs['candidate_pk'])
        previous_commitment_exists = Commitment.objects.filter(proposal=self.proposal,
                                                               authority=self.candidate).exists()
        if previous_commitment_exists:
            raise Http404
        c = get_object_or_404(Candidacy,
                          candidate=self.candidate,
                          user=self.request.user)
        elections_where_the_candidate_cannot_commit = self.candidate.elections.filter(candidates_can_commit_everywhere=False)
        if elections_where_the_candidate_cannot_commit:
            areas = []
            for election in self.candidate.elections.all():
                if election.area:
                    areas.append(election.area)
            if self.proposal.area not in areas:
                raise Http404
            # The former can be refactored

    def get_authority(self):
        return self.candidate


class NotCommitView(CommitView, NotCommitViewBase):
    form_class = VotaInteligenteAuthorityNotCommitingForm

class ThanksForProposingView(ThanksForProposingViewBase):

    def get_context_data(self, **kwargs):
        kwargs = super(ThanksForProposingView, self).get_context_data(**kwargs)
        kwargs['area'] = self.object.area
        return kwargs


class ProposalsPerArea(EmbeddedViewBase, ProposalFilterMixin, ListView):
    template_name = 'popular_proposal/area.html'
    context_object_name = 'popular_proposals'
    filterset_class = ProposalGeneratedAtFilter

    def _get_filterset_kwargs(self):
        return {'area': self.area}

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, id=self.kwargs['slug'])
        return super(ProposalsPerArea, self).dispatch(request, *args, **kwargs)


class WizardWithAreaMixin(object):
    def determine_area(self, data):
        is_testing = data.pop("is_testing", False)
        if 'area' in data.keys():
            return data['area']
        elif hasattr(self, 'area'):
            return self.area
        else:
            return Area.objects.get(id=config.DEFAULT_AREA)

    def apply_extra_kwargs_from_data(self, data):
        return {'area': self.determine_area(data)}

wizard_form_list = get_form_list()

class ProposalWizardDependingOnArea(WizardWithAreaMixin, ProposalWizardBase):
    '''
    Esta es la clase del wizard a la que se llega por hacer
    /propuestas/crear/villarrica
    '''
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, id=self.kwargs['slug'])
        return super(ProposalWizardDependingOnArea, self).dispatch(request, *args, **kwargs)

    def get_form_list(self):
        form_list = OrderedDict()
        previous_forms = self.get_previous_forms()
        my_list = previous_forms + get_form_list(user=self.request.user)
        counter = 0
        for form_class in my_list:
            form_list[str(counter)] = form_class
            counter += 1
        self.form_list = form_list
        return form_list

wizard_initial_form_classes = wizard_previous_form_classes()

class ProposalWizardFull(WizardWithAreaMixin, ProposalWizardBase):
    '''
    Esta es la clase del wizard a la que se llega por hacer
    /propuestas/create_full_wizard
    Acá lo primero que te preguntamos es para qué comuna quieres crear
    la propuesta
    '''
    form_list = wizard_initial_form_classes + wizard_form_list

    def get_previous_forms(self):
        return wizard_initial_form_classes


class ProposalWizardFullWithoutArea(WizardWithAreaMixin, ProposalWizardBase):
    '''
    Esta es la clase del wizard a la que se llega por hacer
    /propuestas/crear
    '''
    form_list = wizard_form_list

    def get_previous_forms(self):
        return []



