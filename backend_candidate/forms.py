# coding=utf-8
from django import forms
from candidator.models import Topic, Position, TakenPosition
from collections import OrderedDict
from django.utils.translation import ugettext as _
from django.conf import settings
from elections.models import PersonalData
import os
from agenda.forms import ActivityForm
from agenda.models import Activity
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe


def get_field_from_topic(topic):
    field = forms.ChoiceField(widget=forms.RadioSelect,
                              required=False)
    field.label = topic.label
    field.description = topic.description
    field.help_text = topic.description
    choices = []
    for position in topic.positions.all():
        choices.append((position.id, mark_safe(position.label)))
    field.choices = choices
    return field


class CandidateTopicFormBase(forms.Form):
    topic_id = forms.IntegerField(widget=forms.HiddenInput)
    answer = forms.ChoiceField(widget=forms.RadioSelect)
    description = forms.CharField(widget=forms.TextInput)

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate')
        super(CandidateTopicFormBase, self).__init__(*args, **kwargs)

    class Meta:
            fields = ('topic_id', 'answer', 'description')

    def save(self):
        position = Position.objects.get(id=self.cleaned_data['answer'])
        topic = Topic.objects.get(id=self.cleaned_data['topic_id'])
        description = self.cleaned_data['description']
        taken_position = TakenPosition(position=position,
                                       topic=topic,
                                       person=self.candidate,
                                       description=description)
        taken_position.save()
        return taken_position


def get_form_class_from_topic(topic):
    class CandidateTopicForm(CandidateTopicFormBase):
        def __init__(self, *args, **kwargs):
            self.topic = topic
            super(CandidateTopicForm, self).__init__(*args, **kwargs)
            self.fields['topic_id'].initial = topic.id
            self.fields['answer'] = get_field_from_topic(topic)

    return CandidateTopicForm


def get_fields_dict_from_topic(topic, taken_position=None):
    dict_ = OrderedDict()
    topic_id = str(topic.id)
    dict_['answer_for_' + topic_id] = get_field_from_topic(topic)
    description_label = _(u'Tus comentarios sobre esta pregunta')
    dict_['description_for_' + topic_id] = forms.CharField(widget=forms.TextInput,
                                                           required=False,
                                                           label=description_label)
    if taken_position and taken_position.position:
        dict_['answer_for_' + topic_id].initial = taken_position.position.id
        dict_['description_for_' + topic_id].initial = taken_position.description
    return dict_

class MediaNaranjaSingleCategoryMixin(object):
    def set_fields_for(self, category):
        for topic in category.topics.all():
            taken_positions = (TakenPosition.
                               objects.filter(topic=topic,
                                              person=self.candidate)
                               ).exists()
            fields_kwargs = {}
            if taken_positions:
                taken_position = (TakenPosition.
                                  objects.get(topic=topic,
                                              person=self.candidate)
                                  )
                fields_kwargs.update({'taken_position':
                                      taken_position})
            field_dict = get_fields_dict_from_topic(topic,
                                                    **fields_kwargs)
            self.fields.update(field_dict)

    def save_answer_for(self, category):
        for topic in category.topics.all():
            topic_key = 'answer_for_' + str(topic.id)
            try:
                topic_id = int(self.cleaned_data[topic_key])
                position = Position.objects.get(id=topic_id)
            except ValueError:
                topic_id = None
                position = None
            description_key = 'description_for_' + str(topic.id)
            description = self.cleaned_data[description_key]
            taken_position, created = (TakenPosition.
                                       objects.
                                       get_or_create(topic=topic,
                                                     person=self.candidate))

            taken_position.position = position
            taken_position.description = description

            taken_position.save()

class MediaNaranjaSingleCandidateMixin(object):
    def __init__(self, *args, **kwargs):

        self.candidate = kwargs.pop('candidate')
        super(MediaNaranjaSingleCandidateMixin, self).__init__(*args, **kwargs)

class MediaNaranjaElectionForm(MediaNaranjaSingleCandidateMixin, forms.Form, MediaNaranjaSingleCategoryMixin):
    def __init__(self, *args, **kwargs):
        super(MediaNaranjaElectionForm, self).__init__(*args, **kwargs)
        for category in self.categories.all():
            self.set_fields_for(category)

    def save(self):
        for category in self.categories.all():
            self.save_answer_for(category)


def get_form_for_election(election):
    class OnDemandMediaNaranjaElectionForm(MediaNaranjaElectionForm):
        def __init__(self, *args, **kwargs):
            self.categories = election.categories
            self.election = election
            super(OnDemandMediaNaranjaElectionForm, self).__init__(*args, **kwargs)

    return OnDemandMediaNaranjaElectionForm


def _import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        try:
            mod = getattr(mod, comp)
        except AttributeError as e:
            raise ImportError
    return mod


class CandidateProfileFormBase(forms.Form):
    image = forms.ImageField(required=False,
                             label=_(u"Imagen de perfil"))
    program_link = forms.URLField(required=False,
                                  label=_(u"Link del programa"),
                                  help_text=_(u"Link a tus ideas y/o planteamientos que quieras que la ciudadanía conozca. Ej: http://micandidatura.cl/mis-ideas/"))

    social_networks = {
        'facebook': {'field': forms.URLField(required=False),
                     'contact_type': 'FACEBOOK',
                     'label': 'Facebook'},
        'twitter': {'field': forms.URLField(required=False),
                    'contact_type': 'TWITTER',
                    'label': 'Twitter'},
        'url': {'field': forms.URLField(required=False),
                'contact_type': 'URL',
                'label': _('Sitio (debe comenzar con http://)')},
    }

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate')
        initial = {}
        for link in self.social_networks:
            contact_type = self.social_networks[link]['contact_type']
            initial[link] = ''
            # Esta wea oficialmente es una chanchería!
            # Si existen varios contact_details para un mismo candidato
            # elige el primero
            # esto está relacionado con #451
            contact_detail = self.candidate.contact_details.filter(contact_type=contact_type).first()
            if contact_detail is not None:
                initial[link] = contact_detail.value
        if 'initial' in kwargs:
            kwargs['initial'].update(initial)
        else:
            kwargs['initial'] = initial
        super(CandidateProfileFormBase, self).__init__(*args, **kwargs)
        for social_network in self.social_networks:
            field_description = self.social_networks[social_network]
            field = field_description['field']
            field.label = field_description['label']
            self.fields[social_network] = field

    def save(self):
        image = self.cleaned_data.pop('image', None)
        if image:
            try:
                path = default_storage.save('tmp/' + image.name, ContentFile(image.read()))
                tmp_file = path
                self.candidate.image = tmp_file
            except:
                pass
            self.candidate.save()
        for link in self.social_networks:
            value = self.cleaned_data.pop(link, None)
            if value:
                contact_type = self.social_networks[link]['contact_type']
                label = self.social_networks[link]['label']
                contact_detail, created = self.candidate.contact_details.get_or_create(contact_type=contact_type)
                contact_detail.value = value
                contact_detail.label = label
                contact_detail.save()
        for field in self.cleaned_data.keys():
            personal_data, created = PersonalData.objects.get_or_create(candidate=self.candidate,
                                                                        label=field)
            personal_data.value = self.cleaned_data[field]
            if personal_data.value is None:
                personal_data.value = ''
            personal_data.save()


def get_candidate_profile_form_class():
    PARENT_FORM_CLASS = CandidateProfileFormBase
    if settings.THEME:
        try:
            PARENT_FORM_CLASS = _import(settings.THEME + ".forms.PersonalDataForm")
        except ImportError as e:
            from votai_general_theme.forms import PersonalDataForm
            PARENT_FORM_CLASS = PersonalDataForm
    else:
        try:
            from votai_general_theme.forms import PersonalDataForm
            PARENT_FORM_CLASS = PersonalDataForm
        except ImportError:
            pass
    cls_attrs = {}
    PARENT_FORM_CLASS = type('CandidateProfileFormBase',
                             (CandidateProfileFormBase,
                              PARENT_FORM_CLASS,
                              object),
                             cls_attrs)
    return PARENT_FORM_CLASS


class CandidateActivityForm(ActivityForm):
    class Meta:
        model = Activity
        fields = ['date', 'url', 'description', 'location']
        labels = {'date': _(u"Fecha"),
                  'url': _(u"Link a tu actividad, puede ser al evento en Facebook"),
                  'description': _(u"Descripción de tu actividad"),
                  'location': _(u"El lugar donde se realizará esta actividad")
                 }
