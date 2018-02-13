# coding=utf-8

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

from popular_proposal.forms import (AuthorityCommitmentForm,
                                    AuthorityNotCommitingForm,
                                    ProposalForm,
                                    UpdateProposalForm,
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
                                                   ProposalFilterMixin)


class WithinAreaProposalCreationView(FormView):
    template_name = 'popular_proposal/create.html'
    form_class = ProposalForm

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
    pass

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