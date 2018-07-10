# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from merepresenta.models import Candidate
from braces.views import StaffuserRequiredMixin
from django.views.generic.base import TemplateView
from django.views import View
from social_core.actions import do_complete
from social_django.views import _do_login
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from social_django.utils import psa


class VolunteerIndexView(StaffuserRequiredMixin, ListView):
    model = Candidate
    template_name = "voluntarios/index.html"
    context_object_name = 'candidates'

    def dispatch(self, *args, **kwargs):
        return super(VolunteerIndexView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = super(VolunteerIndexView, self).get_queryset()
        qs = qs.order_by('-desprivilegio')
        return qs


class VolunteerLoginView(TemplateView):
    template_name = "voluntarios/login.html"


@never_cache
@csrf_exempt
@psa('volunteer_social_complete')
def complete(request, backend, *args, **kwargs):
    return do_complete(request.backend, _do_login, request.user,
                       request=request,
                       *args, **kwargs)