# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from suggestions_for_candidates.models import (IncrementalsCandidateFilter,
                                               ProposalSuggestionForIncremental,
                                               CandidateIncremental,)


class SuggestionsInline(admin.TabularInline):
    model = ProposalSuggestionForIncremental


@admin.register(IncrementalsCandidateFilter)
class IncrementalAdmin(admin.ModelAdmin):
    list_display = ("name","subject")
    inlines = [
        SuggestionsInline
    ]

@admin.register(CandidateIncremental)
class CandidateIncrementalAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'created')
    search_fields = ['candidate__name', ]