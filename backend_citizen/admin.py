from django.contrib import admin
from backend_candidate.models import (Candidacy,
                                      CandidacyContact,
                                      )
from backend_citizen.models import (Profile,)
from django.conf import settings


@admin.register(CandidacyContact)
class CandidacyContactAdmin(admin.ModelAdmin):
    list_display = ('candidate',
                    'mail',
                    'times_email_has_been_sent',
                    'used_by_candidate')
    search_fields = ['candidate__name', "candidate__elections__name", 'mail']
    fields = ('candidate', 'mail', 'initial_password')

    actions = ['send_mail_candidate']

    def save_model(self, request, obj, form, change):

        creating = obj.pk is None
        super(CandidacyContactAdmin, self).save_model(request, obj, form, change)
        if settings.NOTIFY_CANDIDATES and creating:
            obj.send_mail_with_user_and_password()


    def send_mail_candidate(self, request, queryset):
        for contact in queryset.all():
            contact.send_mail_with_user_and_password()
    send_mail_candidate.short_description = u"Mail estos contactos con usuario y password"


@admin.register(Candidacy)
class CandidacyAdmin(admin.ModelAdmin):
    list_display = ('user', 'candidate', 'get_last_log_in', 'get_commited')
    search_fields = ['candidate__name', "candidate__elections__name"]

    def get_last_log_in(self, candidacy):
        return candidacy.user.last_login

    def get_commited(self, candidacy):
        return candidacy.candidate.commitments.exists()


    get_last_log_in.admin_order_field = 'user__last_login'
    get_commited.boolean = True

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_organization')
    search_fields = ['user__username', 'user__email', 'user__first_name']
