
from django.contrib import admin
from elections.models import Election, Candidate, PersonalData, QuestionCategory
from popolo.models import Organization, Membership, ContactDetail, OtherName, Post, Area
from django.contrib.contenttypes.admin import GenericTabularInline
from django import forms
from django.conf import settings
from candidator.models import Position, TakenPosition
from elections.models import Topic


class TakenPositionModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TakenPositionModelForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            positions = self.instance.topic.positions.all()
            self.fields['position'].queryset = positions

    class Meta:
        model = TakenPosition
        fields = ('topic', 'position', 'person')


class TakenPositionInlineModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TakenPositionInlineModelForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            positions_qs = kwargs['instance'].topic.positions.all()
            self.fields['position'].queryset = positions_qs

    class Meta:
        model = TakenPosition
        fields = ('position', 'description')

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(TakenPositionInlineModelForm, self).save(commit=False)
        if m.position is not None:
            m.topic = m.position.topic
        m.save()
        return m


class TakenPositionCandidateInline(admin.TabularInline):
    model = TakenPosition
    form = TakenPositionInlineModelForm
    extra = 0
    can_delete = False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'position':
            pass
        return super(TakenPositionCandidateInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TakenPositionAdmin(admin.ModelAdmin):
    form = TakenPositionModelForm
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
    list_display = ('__str__', 'election')

    def save_model(self, request, obj, form, change):
        creating = not change
        obj.save()
        if creating:
            for candidate in obj.election.candidates.all():
                TakenPosition.objects.get_or_create(topic=obj, person=candidate)

admin.site.register(Topic, TopicAdmin)


class TopicInline(admin.TabularInline):
    model = Topic


class QuestionCategoryAdmin(admin.ModelAdmin):
    inlines = [TopicInline, ]
    list_display = ('__str__', 'election')
admin.site.register(QuestionCategory, QuestionCategoryAdmin)


class QuestionCategoryInline(admin.TabularInline):
    model = QuestionCategory

    list_display = ('__str__', 'election')


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
        TakenPositionCandidateInline,
    ]
    search_fields = ['name', 'election__name']
    ordering = ['name']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(CandidateAdmin, self).get_fieldsets(request, obj)
        if hasattr(request, "_gfs_marker"):
            for key in settings.DEFAULT_CANDIDATE_EXTRA_INFO.keys():
                fieldsets[0][1]['fields'] += (key,)
        setattr(request, "_gfs_marker", 1)
        return fieldsets

    def save_model(self, request, obj, form, change):
        creating = not change
        obj.save()
        if creating:
            for cat in obj.election.categories.all():
                for topic in cat.topics.all():
                    TakenPosition.objects.get_or_create(topic=topic, person=obj)

admin.site.register(Candidate, CandidateAdmin)


class PostAdmin(admin.ModelAdmin):
    pass
admin.site.register(Post, PostAdmin)


class AreaAdmin(admin.ModelAdmin):
    pass
admin.site.register(Area, AreaAdmin)
