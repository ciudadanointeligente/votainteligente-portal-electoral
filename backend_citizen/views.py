# coding=utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from popular_proposal.forms import ProposalTemporaryDataUpdateForm
from popular_proposal.models import (ProposalTemporaryData,
                                     PopularProposal,
                                     ProposalLike)
from django.core.urlresolvers import reverse
from django.views.generic.edit import UpdateView
from backend_citizen.forms import (UserChangeForm,
                                   OrganizationCreationForm,
                                   GroupCreationForm)
from django.contrib.auth.models import User
from backend_citizen.models import Organization
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from registration.backends.hmac.views import RegistrationView
from django.views.generic.list import ListView
from backend_citizen.stats import StatsPerProposal, PerUserTotalStats
from django.views.generic.base import RedirectView


class IndexView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.profile.is_organization:
            return reverse('organization_profiles:update')
        return reverse('backend_citizen:update_my_profile')

class MyProposalsView(TemplateView):
    template_name = 'backend_citizen/my_proposals.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MyProposalsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(MyProposalsView, self).get_context_data(*args, **kwargs)
        context['temporary_proposals'] = ProposalTemporaryData.objects.filter(proposer=self.request.user).order_by('-updated')
        return context


class PopularProposalTemporaryDataUpdateView(LoginRequiredMixin, FormView):
    template_name = 'backend_citizen/temporary_data_update.html'
    form_class = ProposalTemporaryDataUpdateForm

    def get_form_kwargs(self):
        kwargs = super(PopularProposalTemporaryDataUpdateView, self).get_form_kwargs()
        pk = self.kwargs.pop('pk')
        self.temporary_data = ProposalTemporaryData.objects.get(id=pk)
        kwargs['temporary_data'] = self.temporary_data
        kwargs['proposer'] = self.request.user
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(PopularProposalTemporaryDataUpdateView, self).get_context_data(*args, **kwargs)
        context['temporary_data'] = self.temporary_data
        return context

    def get_success_url(self):
        return reverse('backend_citizen:my_proposals')

    def form_valid(self, form):
        form.save()
        return super(PopularProposalTemporaryDataUpdateView, self).form_valid(form)


class UpdateUserView(LoginRequiredMixin, UpdateView):
    form_class = UserChangeForm
    model = User
    template_name = 'backend_citizen/update_my_profile.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('backend_citizen:my_proposals')


class OrganizationDetailView(DetailView):
    model = Organization
    template_name = 'backend_citizen/organization.html'
    context_object_name = 'organization'
    slug_field = 'id'


class OrganizationCreateView(LoginRequiredMixin, CreateView):
    model = Organization
    template_name = 'backend_citizen/create_organization.html'
    form_class = OrganizationCreationForm

    def get_form_kwargs(self):
        kwargs = super(OrganizationCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('backend_citizen:my_proposals')


class DoYouBelongToAnOrgView(LoginRequiredMixin, TemplateView):
    template_name = "backend_citizen/do_you_belong_to_an_org.html"

    def get(self, *args, **kwargs):
        self.request.user.profile.first_time_in_backend_citizen = True
        self.request.user.profile.save()
        return super(DoYouBelongToAnOrgView, self).get(*args, **kwargs)


class GroupRegistrationView(RegistrationView):
    form_class = GroupCreationForm

    def register(self, form):
        new_user = super(GroupRegistrationView, self).register(form)
        return new_user

    def get_success_url(self, user):
        return reverse('registration_activation_complete')

    def create_inactive_user(self, form):
        group = super(GroupRegistrationView, self).create_inactive_user(form)
        form.set_group_profile(group)
        return group


class MySupportsView(LoginRequiredMixin, ListView):
    template_name = 'backend_citizen/my_supports.html'
    model = ProposalLike
    context_object_name = 'supports'

    def get_queryset(self):
        qs = super(MySupportsView, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class MyStats(LoginRequiredMixin, TemplateView):
    template_name = 'backend_citizen/stats.html'

    def get_context_data(self, *args, **kwargs):
        context = super(MyStats, self).get_context_data(*args, **kwargs)
        stats = {}
        proposals = PopularProposal.objects.filter(proposer=self.request.user)
        for proposal in proposals:
            stats[proposal.id] = StatsPerProposal(proposal)
        context['stats'] = stats
        context['total_stats'] = PerUserTotalStats(self.request.user)
        return context
