
from django.contrib import admin
from elections.models import Election, Candidate
from popolo.models import Organization, Membership, ContactDetail, OtherName
from django.contrib.contenttypes.admin import GenericTabularInline
# from django.contrib.flatpages.admin import FlatPageAdmin
# from django.contrib.flatpages.models import FlatPage
## OOPS this is a custom widget that works for initializing
## tinymce instances on stacked and tabular inlines
## for flatpages, just use the tinymce packaged one.
#from content.widgets import TinyMCE
# from tinymce.widgets import TinyMCE


class ElectionAdmin(admin.ModelAdmin):
    search_fields = ['name', 'tags']


admin.site.register(Election, ElectionAdmin)


class OrgnizationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Organization, OrgnizationAdmin)


class ContactDetailInline(GenericTabularInline):
    model = ContactDetail


class MembershipInline(admin.TabularInline):
    model = Membership


class OtherNameInline(GenericTabularInline):
    model = OtherName


class CandidateAdmin(admin.ModelAdmin):
    inlines = [
        ContactDetailInline,
        MembershipInline,
        OtherNameInline
    ]
admin.site.register(Candidate, CandidateAdmin)

# class PageForm(FlatpageForm):
#     class Meta:
#         model = FlatPage
#         widgets = {
#             'content': TinyMCE(),
#         }


# class PageAdmin(FlatPageAdmin):
#     """
#     Page Admin
#     """
#     form = PageForm

# admin.site.unregister(FlatPage)
# admin.site.register(FlatPage, PageAdmin)
