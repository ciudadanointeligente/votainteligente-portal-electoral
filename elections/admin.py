
from django.contrib import admin
from elections.models import Election, Candidate, PersonalData, QuestionCategory
from popolo.models import Organization, Membership, ContactDetail, OtherName, Post, Area
from django.contrib.contenttypes.admin import GenericTabularInline
from django import forms
from django.conf import settings
from candidator.models import Topic, Position, TakenPosition
# from django.contrib.flatpages.admin import FlatPageAdmin
# from django.contrib.flatpages.models import FlatPage
## OOPS this is a custom widget that works for initializing
## tinymce instances on stacked and tabular inlines
## for flatpages, just use the tinymce packaged one.
#from content.widgets import TinyMCE
# from tinymce.widgets import TinyMCE


class TakenPositionAdmin(admin.ModelAdmin):
    pass
admin.site.register(TakenPosition, TakenPositionAdmin)


class TakenPositionInline(admin.TabularInline):
    model = TakenPosition


class PositionAdmin(admin.ModelAdmin):
    inlines = [TakenPositionInline, ]

admin.site.register(Position, PositionAdmin)


class PositionInline(admin.TabularInline):
    model = Position


class TopicAdmin(admin.ModelAdmin):
    inlines = [PositionInline, ]
admin.site.register(Topic, TopicAdmin)


class TopicInline(admin.TabularInline):
    model = Topic


class QuestionCategoryAdmin(admin.ModelAdmin):
    inlines = [TopicInline, ]
admin.site.register(QuestionCategory, QuestionCategoryAdmin)


class QuestionCategoryInline(admin.TabularInline):
    model = QuestionCategory


class CandidateModelForm(forms.ModelForm):
    model = Candidate

    def __init__(self, *args, **kwargs):
        super(CandidateModelForm, self).__init__(*args, **kwargs)
        self.extra_info_fields = settings.DEFAULT_CANDIDATE_EXTRA_INFO.keys()
        for key in self.extra_info_fields:
            self.fields.update({key: forms.CharField(max_length=512,
                                                     label=key,
                                                     required=False,
                                                     widget=forms.TextInput(),
                                                     initial=self.instance.extra_info[key]
                                                     )})

    def save(self, commit=True, *args, **kwargs):
        instance = super(CandidateModelForm, self).save(commit, *args, **kwargs)
        for key in self.extra_info_fields:
            instance.extra_info[key] = self.cleaned_data.get(key, None)
        if commit:
            instance.save()
        return instance


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
    inlines = [QuestionCategoryInline, ]

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
    form = CandidateModelForm
    inlines = [
        ContactDetailInline,
        MembershipInline,
        OtherNameInline,
        PersonalDataInline,
    ]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(CandidateAdmin, self).get_fieldsets(request, obj)
        if hasattr(request, "_gfs_marker"):
            for key in settings.DEFAULT_CANDIDATE_EXTRA_INFO.keys():
                fieldsets[0][1]['fields'] += (key,)
        setattr(request, "_gfs_marker", 1)
        return fieldsets

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
