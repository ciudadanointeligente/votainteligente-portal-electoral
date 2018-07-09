# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from merepresenta.models import Candidate
from braces.views import StaffuserRequiredMixin


class VolunteerIndexView(StaffuserRequiredMixin, ListView):
    model = Candidate
    template_name = "voluntarios/index.html"
    context_object_name = 'candidates'

    def get_queryset(self):
        qs = super(VolunteerIndexView, self).get_queryset()
        qs = qs.order_by('-desprivilegio')
        return qs