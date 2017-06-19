# coding=utf-8

from backend_candidate.models import Candidacy

from constance import config

from django.conf import settings

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.urlresolvers import reverse

from django.http import HttpResponseNotFound, JsonResponse, Http404

from django.shortcuts import get_object_or_404

from django.template.response import TemplateResponse

from django.utils.decorators import method_decorator

from django.utils.translation import ugettext as _

from django.views.generic import View

from django.views.generic.detail import DetailView

from django.views.generic.edit import FormView, UpdateView

from django.views.generic.list import ListView

from django_filters.views import FilterView

from elections.models import Area, Candidate

from popular_proposal.filters import ProposalAreaFilter

from popular_proposal.forms import (CandidateCommitmentForm,
                                    CandidateNotCommitingForm,
                                    ProposalAreaFilterForm,
                                    ProposalFilterForm,
                                    ProposalForm,
                                    UpdateProposalForm,
                                    SubscriptionForm,
                                    )

from popular_proposal.models import (Commitment,
                                     ConfirmationOfProposalTemporaryData,
                                     PopularProposal,
                                     ProposalLike,
                                     ProposalTemporaryData,)

from votainteligente.view_mixins import EmbeddedViewBase


class ProposalCreationView(FormView):
    template_name = 'popular_proposal/create.html'
    form_class = ProposalForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.area = get_object_or_404(Area, id=self.kwargs['slug'])
        return super(ProposalCreationView, self).dispatch(*args, **kwargs)

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
    def dispatch(self, *args, **kwargs):
        self.proposal = get_object_or_404(PopularProposal,
                                          id=self.kwargs['pk'])
        if self.request.method == 'GET':
            self.next_url = self.request.GET.get('next', None)
        elif self.request.method == 'POST':
            self.next_url = self.request.POST.get('next', None)
        return super(SubscriptionView, self).dispatch(*args, **kwargs)

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


class HomeView(EmbeddedViewBase, FilterView):
    model = PopularProposal
    template_name = 'popular_proposal/home.html'
    filter_fields = ['clasification', 'area', ]

    def get_queryset(self):
        qs = super(HomeView, self).get_queryset().exclude(area__id=config.HIDDEN_AREAS)
        return qs

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        initial = self.request.GET
        context['form'] = ProposalFilterForm(initial=initial)
        return context

    def get_context_object_name(self, object_list):
        return 'popular_proposals'


class PopularProposalDetailView(EmbeddedViewBase, DetailView):
    model = PopularProposal
    template_name = 'popular_proposal/detail.html'
    context_object_name = 'popular_proposal'


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


class ProposalsPerArea(EmbeddedViewBase, ListView):
    model = PopularProposal
    template_name = 'popular_proposal/area.html'
    context_object_name = 'popular_proposals'

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, id=self.kwargs['slug'])
        return super(ProposalsPerArea, self).dispatch(request, *args, **kwargs)

    def get_context_data(self):
        context = super(ProposalsPerArea, self).get_context_data()
        initial = self.request.GET or None
        context['form'] = ProposalAreaFilterForm(area=self.area,
                                                 initial=initial)
        return context

    def get_queryset(self):
        kwargs = {'data': self.request.GET or None,
                  'area': self.area
                  }
        filterset = ProposalAreaFilter(**kwargs).qs
        return filterset


class CommitView(FormView):
    template_name = 'popular_proposal/commitment/commit_yes.html'
    form_class = CandidateCommitmentForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
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
        # The following can be refactored
        areas = []
        for election in self.candidate.elections.all():
            if election.area:
                areas.append(election.area)
        if self.proposal.area not in areas:
            return HttpResponseNotFound()
        # The former can be refactored
        return super(CommitView, self).dispatch(*args, **kwargs)

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
        url = reverse('popular_proposals:commitment', kwargs={'candidate_slug': self.candidate.id,
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

    def dispatch(self, *args, **kwargs):
        self.proposal = get_object_or_404(PopularProposal, slug=self.kwargs['proposal_slug'])
        self.candidate = get_object_or_404(Candidate, id=self.kwargs['candidate_slug'])
        return super(CommitmentDetailView, self).dispatch(*args, **kwargs)

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


class ConfirmPopularProposalView(LoginRequiredMixin, DetailView):
    model = ConfirmationOfProposalTemporaryData
    slug_field = 'identifier'
    slug_url_kwarg = 'identifier'
    template_name = 'popular_proposal/confirm.html'

    def get_object(self, *args, **kwargs):
        confirmation = super(ConfirmPopularProposalView, self).get_object(*args, **kwargs)
        if confirmation.temporary_data.proposer != self.request.user:
            raise Http404
        if not confirmation.confirmed:
            confirmation.confirm()
        elif settings.SHOULD_RETURN_404_THE_SECOND_TIME_SOMEONE_CONFIRMS_A_PROPOSAL:
            raise Http404
        return confirmation
