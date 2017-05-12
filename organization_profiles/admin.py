from django.contrib import admin
from organization_profiles.models import (OrganizationTemplate,
                                          BASIC_FIELDS,
                                          ExtraPage,)

# Register your models here.
class OrganizationTemplateAdmin(admin.ModelAdmin):
    fields = BASIC_FIELDS
admin.site.register(OrganizationTemplate, OrganizationTemplateAdmin)

class ExtraPageAdmin(admin.ModelAdmin):
    fields = ["title", "content", "template",   ]
admin.site.register(ExtraPage, ExtraPageAdmin)
