from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from popular_proposal.forms import ProposalTemporaryDataUpdateForm
from popular_proposal.models import ProposalTemporaryData
from django.shortcuts import get_object_or_404


class IndexView(LoginRequiredMixin, TemplateView):
    template_name='backend_citizen/index.html'


class PopularProposalTemporaryDataUpdateView(LoginRequiredMixin, FormView):
    template_name = 'backend_citizen/temporary_data_update.html'
    form_class = ProposalTemporaryDataUpdateForm

    def get_form_kwargs(self):
        kwargs = super(PopularProposalTemporaryDataUpdateView, self).get_form_kwargs()
        pk = self.kwargs.pop('pk')
        self.temporary_data = get_object_or_404(ProposalTemporaryData, pk=pk)
        kwargs['temporary_data'] = self.temporary_data
        kwargs['proposer'] = self.request.user
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(PopularProposalTemporaryDataUpdateView, self).get_context_data(*args, **kwargs)
        context['temporary_data'] = self.temporary_data
        return context
