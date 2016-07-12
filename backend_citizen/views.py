# coding=utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from popular_proposal.forms import ProposalTemporaryDataUpdateForm
from popular_proposal.models import ProposalTemporaryData
from django.core.urlresolvers import reverse
from django.views.generic.edit import UpdateView
from backend_citizen.forms import UserChangeForm, OrganizationCreationForm
from django.contrib.auth.models import User
from backend_citizen.models import Organization
from django.views.generic.edit import CreateView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class IndexView(TemplateView):
    template_name = 'backend_citizen/index.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not self.request.user.profile.first_time_in_backend_citizen:
            return redirect(reverse('backend_citizen:do_you_belong_to_an_org'))
        return super(IndexView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        context['temporary_proposals'] = ProposalTemporaryData.objects.filter(proposer=self.request.user)
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
        return reverse('backend_citizen:index')

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
        return reverse('backend_citizen:index')


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
        return reverse('backend_citizen:index')


class DoYouBelongToAnOrgView(LoginRequiredMixin, TemplateView):
    template_name = "backend_citizen/do_you_belong_to_an_org.html"

    def get(self, *args, **kwargs):
        self.request.user.profile.first_time_in_backend_citizen = True
        self.request.user.profile.save()
        return super(DoYouBelongToAnOrgView, self).get(*args, **kwargs)
