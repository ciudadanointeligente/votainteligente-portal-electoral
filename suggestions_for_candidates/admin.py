# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from suggestions_for_candidates.models import (IncrementalsCandidateFilter,
                                               ProposalSuggestionForIncremental,
                                               CandidateIncremental,)

from django.utils.translation import ugettext_lazy as _
from suggestions_for_candidates.tasks import send_suggestions_tasks


def send_filters_to_candidates(modeladmin, request, queryset):
    for f in queryset.all():
        send_suggestions_tasks.delay(f)
send_filters_to_candidates.short_description = _(u"Enviarle los filtros a los candidatos")


class SuggestionsInline(admin.TabularInline):
    model = ProposalSuggestionForIncremental


@admin.register(IncrementalsCandidateFilter)
class IncrementalAdmin(admin.ModelAdmin):
    list_display = ("name","subject")
    inlines = [
        SuggestionsInline
    ]
    actions = [send_filters_to_candidates]

@admin.register(CandidateIncremental)
class CandidateIncrementalAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'created')
    search_fields = ['candidate__name', ]
