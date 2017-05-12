from django.contrib import admin
from organization_profiles.models import OrganizationTemplate, BASIC_FIELDS

# Register your models here.
class OrganizationTemplateAdmin(admin.ModelAdmin):
    fields = BASIC_FIELDS
admin.site.register(OrganizationTemplate, OrganizationTemplateAdmin)
