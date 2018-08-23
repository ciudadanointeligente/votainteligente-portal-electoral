# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.conf import settings
from merepresenta.models import Candidate

# Register your models here.


class MeRepresentaCandidateAdmin(admin.ModelAdmin):
    list_display = ('name',  'username_do_facebook', 'esta_logado')

    actions = ['send_mail_candidate']

    def esta_logado(self, candidate):
        return candidate.candidacy_set.exists()

    def username_do_facebook(self, candidate):
        if candidate.candidacy_set.exists():
            return candidate.candidacy_set.first().user.username
        return ""
        # return candidate.candidacy_set.first().user.username

    def apagar_datos(self, request, queryset):
        for candidate in queryset.all():
            User.objects.filter(candidacies__candidate=candidate)
            candidate.candidacy_set.all().delete()
            candidate.lgbt_desc.all().delete()
            candidate.taken_positions.all().delete()
            candidate.candidatequestioncategory_set.all().delete()
        send_mail_candidate.short_description = u"Apagar dados de candidatas seleccionadas"

    esta_logado.boolean = True

admin.site.register(Candidate, MeRepresentaCandidateAdmin)