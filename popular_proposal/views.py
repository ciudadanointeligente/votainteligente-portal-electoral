from django.views.generic.edit import FormView
from popular_proposal.forms import ProposalForm
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from popolo.models import Area

# Create your views here.
class ProposalCreationView(FormView):
    template_name = 'popular_proposal/create.html'
    form_class = ProposalForm

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

