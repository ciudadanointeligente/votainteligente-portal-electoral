# coding=utf-8
from collections import OrderedDict

from backend_candidate.models import is_candidate

from constance import config

from django.conf import settings

from django.contrib.auth.decorators import login_required

from django.http import HttpResponseNotFound

from django.shortcuts import get_object_or_404, render

from django.utils.decorators import method_decorator

from elections.models import Area

from formtools.wizard.views import SessionWizardView

from popular_proposal.forms import (UpdateProposalForm,
                                    get_form_list,)

from popular_proposal.models import (ProposalTemporaryData)

from popular_proposal import send_mails_to_staff, wizard_previous_form_classes

wizard_form_list = get_form_list()



class DeterminingKwargsMixin(object):
    def apply_extra_kwargs_from_data(self, data):
        return {}
    

class ProposalWizardBase(SessionWizardView, DeterminingKwargsMixin):
    form_list = wizard_form_list
    model = ProposalTemporaryData
    template_name = 'popular_proposal/wizard/form_step.html'

    def get_template_names(self):
        form = self.get_form(step=self.steps.current)
        template_name = getattr(form, 'template', self.template_name)
        return template_name

    def get_previous_forms(self):
        return []

    def done(self, form_list, **kwargs):
        data = {}
        [data.update(form.cleaned_data) for form in form_list]
        kwargs = {
            'proposer': self.request.user,
            'data': data
        }
        kwargs.update(self.apply_extra_kwargs_from_data(data))
        temporary_data = self.model.objects.create(**kwargs)
        context = self.get_context_data(form=None)
        context.update({'popular_proposal': temporary_data})
        context.update(kwargs)
        if not settings.MODERATION_ENABLED:
            temporary_data.create_proposal()
            context['form_update'] = UpdateProposalForm(instance=temporary_data.created_proposal)
        else:
            temporary_data.notify_new()
        send_mails_to_staff({'temporary_data': temporary_data},
                            'notify_staff_new_proposal')
        return render(self.request, 'popular_proposal/wizard/done.html', context)

    def get_context_data(self, form, **kwargs):
        context = super(ProposalWizardBase, self).get_context_data(form,
                                                                   **kwargs)
        data = self.get_all_cleaned_data()
        if data:
            context.update(self.apply_extra_kwargs_from_data(data))
        context['preview_data'] = data
        return context

    def get_form_kwargs(self, step=None):
        kwargs = super(ProposalWizardBase, self).get_form_kwargs(step)
        kwargs['is_staff'] = self.request.user.is_staff
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_candidate(request.user):
            return HttpResponseNotFound()
        if config.PROPOSALS_ENABLED:
            return super(ProposalWizardBase, self).dispatch(request,
                                                            *args,
                                                            **kwargs)
        else:
            return HttpResponseNotFound()


class ProposalWizard(ProposalWizardBase):
    '''
    Esta es la clase del wizard a la que se llega por hacer
    /propuestas/crea/
    '''
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProposalWizard, self).dispatch(request, *args, **kwargs)

    def get_form_list(self):
        form_list = OrderedDict()
        previous_forms = self.get_previous_forms()
        my_list = previous_forms + get_form_list(user=self.request.user)
        counter = 0
        for form_class in my_list:
            form_list[str(counter)] = form_class
            counter += 1
        self.form_list = form_list
        return form_list