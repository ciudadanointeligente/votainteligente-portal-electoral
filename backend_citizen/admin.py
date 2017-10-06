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
    search_fields = ['candidate__name', "candidate__elections__name", 'mail']


@admin.register(Candidacy)
class CandidacyAdmin(admin.ModelAdmin):
    list_display = ('user', 'candidate', 'created', 'updated', 'get_last_log_in')
    search_fields = ['candidate__name', "candidate__elections__name"]

    def get_last_log_in(self, candidacy):
        return candidacy.user.last_login

    get_last_log_in.admin_order_field = 'user__last_login'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_organization')
    search_fields = ['user__username', 'user__email', 'user__first_name']
