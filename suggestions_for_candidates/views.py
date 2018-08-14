# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from suggestions_for_candidates.models import CandidateIncremental
from django.views.generic.detail import DetailView
from django.contrib.sites.models import Site
from django.conf import settings
from constance import config


class CandidateIncrementalDetailView(DetailView):
    model = CandidateIncremental
    slug_url_kwarg = "identifier"
    slug_field = 'identifier'
    

    def get_queryset(self):
        qs = super(CandidateIncrementalDetailView, self).get_queryset()
        return qs


    def get_context_data(self, **kwargs):
        context = super(CandidateIncrementalDetailView, self).get_context_data(**kwargs)
        context['formset'] = self.object.formset
        context['candidate_incremental'] = self.object
        context['site'] = Site.objects.get_current()
        context['text'] = self.object.suggestion.text
        context['candidate'] = self.object.candidate
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.used = True
        self.object.save()
        CommitmentIcrementalFormset = self.object._formset_class
        formset = CommitmentIcrementalFormset(request.POST, request.FILES)
        if formset.is_valid():
            commitments = formset.save()
            if commitments:
                return render(request, 'backend_candidate/thanks_for_commiting.html', context={'commitments': commitments})
        return self.get(request, *args, **kwargs)

    def get_template_names(self):
        if settings.DEBUG and config.SHOW_MAIL_NOT_TEMPLATE:
            return ['mails/suggestions_for_candidates/body.html']
        return ['backend_candidate/suggestions_for_candidate.html']

