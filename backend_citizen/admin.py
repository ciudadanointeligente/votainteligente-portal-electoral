from django.contrib import admin
from backend_candidate.models import Candidacy
# Register your models here.


@admin.register(Candidacy)
class CandidacyAdmin(admin.ModelAdmin):
    list_display = ('user', 'candidate', 'created', 'updated')