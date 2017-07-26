from popular_proposal.views.wizard import ProposalWizardBase
from votita.forms.forms import wizard_forms_fields
from popular_proposal.forms import (get_form_list,)


wizard_form_list = get_form_list(wizard_forms_fields=wizard_forms_fields)


class VotitaWizard(ProposalWizardBase):
    form_list = wizard_form_list
    template_name = 'popular_proposal/wizard/form_step.html'
