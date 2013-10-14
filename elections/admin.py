
from django.contrib import admin
from elections.models import Election
from django.contrib.flatpages.admin import FlatpageForm, FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
## OOPS this is a custom widget that works for initializing
## tinymce instances on stacked and tabular inlines
## for flatpages, just use the tinymce packaged one.
#from content.widgets import TinyMCE 
from tinymce.widgets import TinyMCE

class ElectionAdmin(admin.ModelAdmin):
	search_fields = ['name', 'tags']
	
admin.site.register(Election, ElectionAdmin)




class PageForm(FlatpageForm):

    class Meta:
        model = FlatPage
        widgets = {
            'content' : TinyMCE(),
        }


class PageAdmin(FlatPageAdmin):
    """
    Page Admin
    """
    form = PageForm

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, PageAdmin)
