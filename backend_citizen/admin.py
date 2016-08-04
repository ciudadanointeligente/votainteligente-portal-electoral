from django.contrib import admin
from backend_candidate.models import Candidacy, CandidacyContact


@admin.register(CandidacyContact)
class CandidacyContactAdmin(admin.ModelAdmin):
    list_display = ('candidate',
                    'mail',
                    'times_email_has_been_sent',
                    'used_by_candidate')


@admin.register(Candidacy)
class CandidacyAdmin(admin.ModelAdmin):
    list_display = ('user', 'candidate', 'created', 'updated')