# coding=utf-8
from django.contrib import admin
from backend_candidate.models import (
                                      IncrementalsCandidateFilter,
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