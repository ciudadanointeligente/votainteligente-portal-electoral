
from django.contrib import admin
from elections.models import Election, Candidate, PersonalData
from popolo.models import Organization, Membership, ContactDetail, OtherName, Post, Area
from django.contrib.contenttypes.admin import GenericTabularInline
from django import forms
from django.conf import settings
# from django.contrib.flatpages.admin import FlatPageAdmin
# from django.contrib.flatpages.models import FlatPage
## OOPS this is a custom widget that works for initializing
## tinymce instances on stacked and tabular inlines
## for flatpages, just use the tinymce packaged one.
#from content.widgets import TinyMCE
# from tinymce.widgets import TinyMCE


class ElectionModelForm(forms.ModelForm):
    model = Election

    def __init__(self, *args, **kwargs):
        super(ElectionModelForm, self).__init__(*args, **kwargs)
        self.extra_info_fields = settings.DEFAULT_ELECTION_EXTRA_INFO.keys()
        for key in self.extra_info_fields:
            self.fields.update({key: forms.CharField(max_length=512,
                                                     label=key,
                                                     required=False,
                                                     widget=forms.TextInput(),
                                                     initial=self.instance.extra_info[key]
                                                     )})

    def save(self, commit=True, *args, **kwargs):
        instance = super(ElectionModelForm, self).save(commit, *args, **kwargs)
        for key in self.extra_info_fields:
            instance.extra_info[key] = self.cleaned_data.get(key, None)
        if commit:
            instance.save()
        return instance


class ElectionAdmin(admin.ModelAdmin):
    form = ElectionModelForm
    search_fields = ['name', 'tags']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(ElectionAdmin, self).get_fieldsets(request, obj)
        if hasattr(request, "_gfs_marker"):
            for key in settings.DEFAULT_ELECTION_EXTRA_INFO.keys():
                fieldsets[0][1]['fields'] += (key,)
        setattr(request, "_gfs_marker", 1)
        return fieldsets

admin.site.register(Election, ElectionAdmin)


class OrgnizationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Organization, OrgnizationAdmin)


class ContactDetailInline(GenericTabularInline):
    model = ContactDetail
    fields = ('label', 'contact_type', 'value')


class MembershipInline(admin.TabularInline):
    model = Membership
    fields = ('label', 'role', 'organization', 'on_behalf_of', 'post', 'start_date', 'end_date', 'area')


class OtherNameInline(GenericTabularInline):
    model = OtherName


class PersonalDataInline(admin.TabularInline):
    model = PersonalData


class CandidateAdmin(admin.ModelAdmin):
    inlines = [
        ContactDetailInline,
        MembershipInline,
        OtherNameInline,
        PersonalDataInline,
    ]
admin.site.register(Candidate, CandidateAdmin)


class PostAdmin(admin.ModelAdmin):
    pass
admin.site.register(Post, PostAdmin)


class AreaAdmin(admin.ModelAdmin):
    pass
admin.site.register(Area, AreaAdmin)
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
