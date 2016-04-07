from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from popular_proposal.forms import ProposalTemporaryDataUpdateForm
from popular_proposal.models import ProposalTemporaryData
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse


class IndexView(LoginRequiredMixin, TemplateView):
    template_name='backend_citizen/index.html'

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
