# coding=utf-8

from backend_candidate.models import Candidacy

from constance import config

import copy

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.http import HttpResponseNotFound, JsonResponse, HttpResponse

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

from popular_proposal.filters import (ProposalWithoutAreaFilter,
                                      ProposalGeneratedAtFilter)

from popular_proposal.forms import (CandidateCommitmentForm,
                                    CandidateNotCommitingForm,
                                    ProposalForm,
                                    UpdateProposalForm,
                                    SubscriptionForm,
                                    )

from popular_proposal.models import (Commitment,
                                     PopularProposal,
                                     ProposalLike,
                                     ProposalTemporaryData,)

from votai_utils.view_mixins import EmbeddedViewBase
import random
from django.conf import settings


class ProposalCreationView(FormView):
    template_name = 'popular_proposal/create.html'
    form_class = ProposalForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, id=self.kwargs['slug'])
        return super(ProposalCreationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(ProposalCreationView, self).get_context_data(**kwargs)
        kwargs['area'] = self.area
        return kwargs

    def get_form_kwargs(self):
        kwargs = super(ProposalCreationView, self).get_form_kwargs()
        kwargs['proposer'] = self.request.user
        kwargs['area'] = self.area
        return kwargs

    def form_valid(self, form):
        self.proposal = form.save()
        return super(ProposalCreationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('popular_proposals:thanks',
                       kwargs={'pk': self.proposal.id})


class ThanksForProposingView(DetailView):
    model = ProposalTemporaryData
    template_name = 'popular_proposal/thanks.html'
    context_object_name = 'proposal'

    def get_context_data(self, **kwargs):
        kwargs = super(ThanksForProposingView, self).get_context_data(**kwargs)
        kwargs['area'] = self.object.area
        return kwargs


class SubscriptionView(FormView):
    template_name = 'popular_proposal/new_subscription.html'
    form_class = SubscriptionForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.proposal = get_object_or_404(PopularProposal,
                                          id=self.kwargs['pk'])
        if self.request.method == 'GET':
            self.next_url = self.request.GET.get('next', None)
        elif self.request.method == 'POST':
            self.next_url = self.request.POST.get('next', None)
        return super(SubscriptionView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SubscriptionView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['proposal'] = self.proposal
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super(SubscriptionView, self).get_context_data(**kwargs)
        kwargs['proposal'] = self.proposal
        if self.next_url:
            kwargs['next'] = self.next_url
        return kwargs

    def form_valid(self, form):
        like = form.subscribe()
        context = self.get_context_data()
        context['like'] = like
        return TemplateResponse(self.request,
                                'popular_proposal/subscribing_result.html',
                                context)


class PopularProposalDetailView(EmbeddedViewBase, DetailView):
    model = PopularProposal
    template_name = 'popular_proposal/detail.html'
    context_object_name = 'popular_proposal'
    layout = "basewithnofixed_navbar.html"


class PopularProposalAyuranosView(DetailView):
    model = PopularProposal
    template_name = 'popular_proposal/ayuranos.html'
    context_object_name = 'popular_proposal'

    def get_context_data(self, **kwargs):
        context = super(PopularProposalAyuranosView, self).get_context_data(**kwargs)
        candidates_qs = Candidate.objects.exclude(commitments__proposal__id=self.object.id).order_by('created_at')
        if settings.PRIORITY_CANDIDATES:
            candidates_qs = candidates_qs.filter(id__in=settings.PRIORITY_CANDIDATES)
        context['candidates'] = candidates_qs
        return context


class PopularProposalDetailRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        proposal = get_object_or_404(PopularProposal, pk=kwargs['pk'])
        return proposal.get_absolute_url()


class PopularProposalOGImageView(DetailView):
    model = PopularProposal

    def render_to_response(self, context, **response_kwargs):
        im = self.object.generate_og_image()
        response = HttpResponse( content_type="image/png")
        im.save(response, "PNG")
        return response


class UnlikeProposalView(View):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseNotFound()
        self.pk = self.kwargs.pop('pk')
        self.like = get_object_or_404(ProposalLike,
                                      pk=self.pk,
                                      user=self.request.user)
        return super(UnlikeProposalView, self).dispatch(request,
                                                        *args,
                                                        **kwargs)

    def post(self, request, **kwargs):
        self.like.delete()
        return JsonResponse({'deleted_item': self.pk})


class ProposalFilterMixin(object):
    model = PopularProposal
    filterset_class = ProposalGeneratedAtFilter
    order_by = None

    def _get_filterset(self):
        initial = copy.copy(self.request.GET) or {}
        filterset_kwargs = self._get_filterset_kwargs()
        filterset_kwargs.update({'data': initial})
        filterset = self.filterset_class(**filterset_kwargs)
        return filterset

    def _get_filterset_kwargs(self):
        return {}

    def get_form(self):
        f = self._get_filterset().form
        return f

    def get_queryset(self):
        return self._get_filterset().qs

    def get_context_data(self, **kwargs):
        context = super(ProposalFilterMixin, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context
#    def get_queryset(self):
#        qs = self.model.ordered.by_likers().exclude(area__id=config.HIDDEN_AREAS)
#        return qs


class HomeView(EmbeddedViewBase, ProposalFilterMixin, FilterView):
    template_name = 'popular_proposal/home.html'
    filterset_class = ProposalGeneratedAtFilter
    context_object_name = 'popular_proposals'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['form_type'] = random.randint(0,1)
        return context


class ProposalsPerArea(EmbeddedViewBase, ProposalFilterMixin, ListView):
    template_name = 'popular_proposal/area.html'
    context_object_name = 'popular_proposals'
    filterset_class = ProposalWithoutAreaFilter

    def _get_filterset_kwargs(self):
        return {'area': self.area}

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, id=self.kwargs['slug'])
        return super(ProposalsPerArea, self).dispatch(request, *args, **kwargs)


class CommitView(FormView):
    template_name = 'popular_proposal/commitment/commit_yes.html'
    form_class = CandidateCommitmentForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not config.PROPOSALS_ENABLED:
            return HttpResponseNotFound()
        self.proposal = get_object_or_404(PopularProposal,
                                          id=self.kwargs['proposal_pk'])
        self.candidate = get_object_or_404(Candidate,
                                           id=self.kwargs['candidate_pk'])
        previous_commitment_exists = Commitment.objects.filter(proposal=self.proposal,
                                                               candidate=self.candidate).exists()
        if previous_commitment_exists:
            return HttpResponseNotFound()
        get_object_or_404(Candidacy,
                          candidate=self.candidate,
                          user=self.request.user)
        elections_where_the_candidate_cannot_commit = self.candidate.elections.filter(candidates_can_commit_everywhere=False)
        if elections_where_the_candidate_cannot_commit:
            areas = []
            for election in self.candidate.elections.all():
                if election.area:
                    areas.append(election.area)
            if self.proposal.area not in areas:
                return HttpResponseNotFound()
            # The former can be refactored
        return super(CommitView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.commitment = form.save()
        if self.commitment.commited:
            messages.add_message(self.request,
                                 messages.SUCCESS,
                                 _(u'Muchas gracias por tu compromiso, le hemos enviado un mail a los ciudadanos que apoyan esta propuesta así como a aquel que la realizó.'))
        else:
            messages.add_message(self.request,
                                 messages.WARNING,
                                 _(u'Muchas gracias por tu sinceridad. Le hemos enviado un mail a los ciudadanos que apoyan y además a aquel que la realizó.'))
        return super(CommitView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CommitView, self).get_form_kwargs()
        kwargs['proposal'] = self.proposal
        kwargs['candidate'] = self.candidate
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CommitView, self).get_context_data(**kwargs)
        context['proposal'] = self.proposal
        context['candidate'] = self.candidate
        return context

    def get_success_url(self):
        url = reverse('popular_proposals:commitment', kwargs={'candidate_slug': self.candidate.slug,
                                                              'proposal_slug': self.proposal.slug})
        return url


class NotCommitView(CommitView):
    template_name = 'popular_proposal/commitment/commit_no.html'
    form_class = CandidateNotCommitingForm


class CommitmentDetailView(DetailView):
    model = Commitment
    # template_name = 'popular_proposal/commitment/detail_yes.html'

    def get_template_names(self):
        if self.object.commited:
            return 'popular_proposal/commitment/detail_yes.html'
        else:
            return 'popular_proposal/commitment/detail_no.html'

    def dispatch(self, request, *args, **kwargs):
        self.proposal = get_object_or_404(PopularProposal, slug=self.kwargs['proposal_slug'])
        self.candidate = get_object_or_404(Candidate, slug=self.kwargs['candidate_slug'])
        return super(CommitmentDetailView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, candidate=self.candidate, proposal=self.proposal)


class PopularProposalUpdateView(UpdateView):
    form_class = UpdateProposalForm
    template_name = 'popular_proposal/update.html'
    model = PopularProposal
    context_object_name = 'popular_proposal'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PopularProposalUpdateView, self).dispatch(request,
                                                               *args,
                                                               **kwargs)

    def get_queryset(self):
        qs = super(PopularProposalUpdateView, self).get_queryset()
        qs = qs.filter(proposer=self.request.user)
        return qs
