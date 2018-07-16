# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from merepresenta.models import Candidate, VolunteerInCandidate
from braces.views import StaffuserRequiredMixin
from django.views.generic.base import TemplateView
from django.views import View
from social_core.actions import do_complete
from social_django.views import _do_login
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from social_django.utils import psa, STORAGE, get_strategy
from django.views.generic.edit import FormView
from merepresenta.voluntarios.forms import AddCandidacyContactForm
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404


class VolunteerIndexView(StaffuserRequiredMixin, ListView):
    model = Candidate
    login_url = reverse_lazy(u"volunteer_login")
    template_name = "voluntarios/index.html"
    context_object_name = 'candidates'

    def get_queryset(self):
        qs = super(VolunteerIndexView, self).get_queryset()
        qs = qs.exclude(contacts__isnull=False).order_by('-desprivilegio')
        return qs


class VolunteerLoginView(TemplateView):
    template_name = "voluntarios/login.html"



def load_strategy(request=None):
    return get_strategy('merepresenta.voluntarios.strategy.VolunteerStrategy', STORAGE, request)

@never_cache
@csrf_exempt
@psa(load_strategy=load_strategy)
def complete(request, backend, *args, **kwargs):
    return do_complete(request.backend, _do_login, request.user,
                       redirect_value='volunteer_login', request=request,
                       *args, **kwargs)


class AddMailToCandidateView(StaffuserRequiredMixin, FormView):
    form_class = AddCandidacyContactForm
    login_url = reverse_lazy(u"volunteer_login")
    template_name = 'voluntarios/add_email_to_candidate.html'
    
    def get_success_url(self): 
        return reverse_lazy('obrigado')

    def dispatch(self, *args, **kwargs):
        slug = kwargs['slug']
        self.candidate = get_object_or_404(Candidate, slug=slug)
        if self.request.user.is_authenticated() and self.request.user.is_staff:
            self.record = VolunteerInCandidate.objects.get_or_create(candidate=self.candidate,
                                                                     volunteer=self.request.user)
        return super(AddMailToCandidateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AddMailToCandidateView, self).get_form_kwargs()

        kwargs['candidate'] = self.candidate
        kwargs['volunteer'] = self.request.user
        return kwargs



class ObrigadoView(StaffuserRequiredMixin, TemplateView):
    template_name=u'voluntarios/obrigado.html'