from django.contrib import admin
from preguntales.models import Message, Answer

class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ['content','person']
    extra = 0



class MensajesAdmin(admin.ModelAdmin):
    fields = ['author_name','author_email', 'subject', 'content', 'people']
    list_filter = ()
    search_fields = ['author_name', 'author_email', 'subject', 'people__name']
    inlines = [AnswerInline]

    actions = ['accept_moderation']

    def accept_moderation(self, request, queryset):
        for message in queryset:
            message.accept_moderation()
    accept_moderation.short_description = "Aceptar Mensajes para ser enviados"

admin.site.register(Message, MensajesAdmin)

