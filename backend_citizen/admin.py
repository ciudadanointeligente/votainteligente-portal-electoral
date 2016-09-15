from django.contrib import admin
from backend_candidate.models import (Candidacy,
                                      CandidacyContact,
                                      )
from backend_citizen.models import (Profile,)


@admin.register(CandidacyContact)
class CandidacyContactAdmin(admin.ModelAdmin):
    list_display = ('candidate',
                    'mail',
                    'times_email_has_been_sent',
                    'used_by_candidate')


@admin.register(Candidacy)
class CandidacyAdmin(admin.ModelAdmin):
    list_display = ('user', 'candidate', 'created', 'updated')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_journalist')
    search_fields = ['user__username', 'user__email', 'user__first_name']