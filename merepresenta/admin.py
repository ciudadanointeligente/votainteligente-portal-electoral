# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.conf import settings
from merepresenta.models import Candidate, CandidateQuestionCategory
from django.contrib.auth.models import User

# Register your models here.


class MeRepresentaCandidateAdmin(admin.ModelAdmin):
    list_display = ('name',  'username_do_facebook', 'esta_logado')

    actions = ['apagar_datos']
    search_fields = ['name',]

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
            candidate.lgbt_desc.clear()
            candidate.taken_positions.all().delete()
            candidate.candidatequestioncategory_set.all().delete()

    apagar_datos.short_description = u"Apagar dados de candidatas seleccionadas"

    esta_logado.boolean = True
    esta_logado.admin_order_field = 'candidacy__user__last_login'

admin.site.register(Candidate, MeRepresentaCandidateAdmin)



class CandidateQuestionCategoryAdmin(admin.ModelAdmin):
    pass

    search_fields = ['candidate__name',]

admin.site.register(CandidateQuestionCategory, CandidateQuestionCategoryAdmin)