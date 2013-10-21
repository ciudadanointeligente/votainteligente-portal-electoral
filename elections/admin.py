
from django.contrib import admin
from elections.models import Election, VotaInteligenteMessage, VotaInteligenteAnswer, CandidatePerson
from django.contrib.flatpages.admin import FlatpageForm, FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
## OOPS this is a custom widget that works for initializing
## tinymce instances on stacked and tabular inlines
## for flatpages, just use the tinymce packaged one.
#from content.widgets import TinyMCE 
from tinymce.widgets import TinyMCE
from django.utils.translation import ugettext_lazy as _

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

class AnswerInline(admin.TabularInline):
    model = VotaInteligenteAnswer
    fields = ['content','person']
    extra = 0

class CandidatePersonExtraInfoAdmin(admin.ModelAdmin):
    readonly_fields = ('person',)
    fields = ('reachable', )
    search_fields = ['person__name', 'person__api_instance__election__name']

admin.site.register(CandidatePerson, CandidatePersonExtraInfoAdmin)


class MensajesAdmin(admin.ModelAdmin):
    fields = ['author_name','author_email', 'subject', 'content', 'people', 'moderated']
    list_filter = ('moderated', )
    inlines = [
    AnswerInline
    ]

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('moderated__exact'):
            q = request.GET.copy()
            q['moderated__exact'] = 0
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(MensajesAdmin,self).changelist_view(request, extra_context=extra_context)

    actions = ['accept_moderation']

    def accept_moderation(self, request, queryset):
        for message in queryset:
            message.accept_moderation()
    accept_moderation.short_description = "Aceptar Mensajes para ser enviados"

admin.site.register(VotaInteligenteMessage, MensajesAdmin)