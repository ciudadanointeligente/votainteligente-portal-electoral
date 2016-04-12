from django.views.generic.edit import FormView
from popular_proposal.forms import ProposalForm, SubscriptionForm
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from popolo.models import Area
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from popular_proposal.models import PopularProposal


class ProposalCreationView(FormView):
    template_name = 'popular_proposal/create.html'
    form_class = ProposalForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.area = get_object_or_404(Area, id=self.kwargs['pk'])
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
        form.save()
        return super(ProposalCreationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('popular_proposals:thanks', kwargs={'pk': self.area.id})


class ThanksForProposingView(TemplateView):
    template_name = 'popular_proposal/thanks.html'


class SubscriptionView(FormView):
    template_name = 'popular_proposal/new_subscription.html'
    form_class = SubscriptionForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.proposal = get_object_or_404(PopularProposal, id=self.kwargs['pk'])
        return super(SubscriptionView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SubscriptionView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['proposal'] = self.proposal
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super(SubscriptionView, self).get_context_data(**kwargs)
        kwargs['proposal'] = self.proposal
        return kwargs

    def get_success_url(self):
        return reverse('area',kwargs={'slug':self.proposal.area.id})

    def form_valid(self, form):
        form.subscribe()
        return super(SubscriptionView, self).form_valid(form)

