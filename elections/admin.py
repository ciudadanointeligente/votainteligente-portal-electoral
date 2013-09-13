from django.contrib import admin
from elections.models import Election

class ElectionAdmin(admin.ModelAdmin):
	search_fields = ['name', 'tags']
	
admin.site.register(Election, ElectionAdmin)
