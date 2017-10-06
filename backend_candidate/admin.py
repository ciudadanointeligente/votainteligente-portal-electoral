# coding=utf-8
from django.contrib import admin
from backend_candidate.models import (
                                      IncrementalsCandidateFilter,
                                      ProposalSuggestionForIncremental,)


class SuggestionsInline(admin.TabularInline):
	model = ProposalSuggestionForIncremental


@admin.register(IncrementalsCandidateFilter)
class IncrementalAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [
        SuggestionsInline
    ]
