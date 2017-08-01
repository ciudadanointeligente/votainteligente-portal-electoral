from popular_proposal.views.wizard import ProposalWizardBase
from votita.forms.forms import wizard_forms_fields
from popular_proposal.forms import (get_form_list,)
from django.views.generic.edit import CreateView, UpdateView
from votita.models import KidsProposal, KidsGathering
from django.forms import inlineformset_factory
from django.views.generic.base import View
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse


wizard_form_list = get_form_list(wizard_forms_fields=wizard_forms_fields)


class VotitaWizard(ProposalWizardBase):
    form_list = wizard_form_list
    template_name = 'popular_proposal/wizard/form_step.html'


class CreateGatheringView(CreateView):
    model = KidsGathering
    template_name = 'votita/create_gathering.html'
    fields = ['name',]

    def get_success_url(self):
        return reverse('votita:proposal_for_gathering',
                      kwargs={'pk':self.object.id})



ProposalFormSet = inlineformset_factory(KidsGathering,
                                        KidsProposal,
                                        fields=('title',))


class CreateProposalsForGathering(UpdateView):
    model = KidsGathering
    template_name = 'votita/agregar_propuestas_a_encuentro.html'
    fields = []
    success_url = 'votita:proposal_for_gathering'

    def get_context_data(self, *args, **kwargs):
        context = super(CreateProposalsForGathering, self).get_context_data(*args, **kwargs)

        if self.request.POST:
            context['formset'] = ProposalFormSet(self.request.POST, instance=self.object)
            context['formset'].full_clean()
        else:
            context['formset'] = ProposalFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        print formset.errors
        if formset.is_valid():
            self.object = form.save()
            proposals = formset.save(commit=False)
            for proposal in proposals:
                proposal.proposer = self.request.user
                proposal.save()
            return redirect(reverse(self.success_url, kwargs={'pk': self.object.pk}))
        else:
            return self.render_to_response(self.get_context_data(form=form))
