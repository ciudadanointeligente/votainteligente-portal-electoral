from django.contrib import admin
from agenda.models import Activity
# Register your models here.


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date')
