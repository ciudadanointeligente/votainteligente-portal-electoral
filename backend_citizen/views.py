from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, CreateView
from popular_proposal.forms import ProposalTemporaryDataUpdateForm
from popular_proposal.models import ProposalTemporaryData
from django.core.urlresolvers import reverse
from popolo.models import Organization
from backend_citizen.forms import OrganizationForm


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'backend_citizen/index.html'

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


class OrganizationCreateView(LoginRequiredMixin, CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'backend_citizen/create_organization.html'

    def get_form_kwargs(self):
        kwargs = super(OrganizationCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('backend_citizen:index')
