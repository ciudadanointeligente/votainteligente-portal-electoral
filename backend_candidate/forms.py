# coding=utf-8
from django import forms
from candidator.models import Topic, Position, TakenPosition
from collections import OrderedDict
from django.utils.translation import ugettext as _
from django.conf import settings
from elections.models import PersonalData
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from popular_proposal.models import Commitment
from django.forms import formset_factory
from django.forms import BaseFormSet


def get_field_from_topic(topic):
    field = forms.ChoiceField(widget=forms.RadioSelect,
                              required=False)
    field.label = topic.label
    choices = []
    for position in topic.positions.all():
        choices.append((position.id, position.label))
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


def get_form_for_election(election):
    class MediaNaranjaElectionForm(forms.Form):
        def __init__(self, *args, **kwargs):
            self.candidate = kwargs.pop('candidate')
            self.election = election
            super(MediaNaranjaElectionForm, self).__init__(*args, **kwargs)
            for category in election.categories.all():
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

        def save(self):
            for category in self.election.categories.all():
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

    return MediaNaranjaElectionForm


def _import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        try:
            mod = getattr(mod, comp)
        except AttributeError:
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
                'label': 'Sitio (debe comenzar con http://)'},
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
            path = default_storage.save('tmp/' + image.name, ContentFile(image.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            self.candidate.image = tmp_file
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
            
        except ImportError:
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


class SimpleCommitmentForm(forms.Form):
    commited = forms.NullBooleanField(label=u"Me comprometo con esta propuesta.",
                                      widget=forms.CheckboxInput,
                                      required=False)
    detail = forms.CharField(widget=forms.Textarea,
                             label=u"Términos en los cuales me comprometo",
                             required=False)

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate')
        self.proposal = kwargs.pop('proposal')
        self.summary = kwargs.pop('summary', None)
        return super(SimpleCommitmentForm, self).__init__(*args, **kwargs)

    def save(self):
        initial_commitment_kwargs = {"proposal": self.proposal, "candidate": self.candidate}
        if self.cleaned_data['commited'] and not Commitment.objects.filter(**initial_commitment_kwargs):
            initial_commitment_kwargs.update(**self.cleaned_data)
            return Commitment.objects.create(**initial_commitment_kwargs)

def get_multi_commitment_forms(candidate, proposals, summaries):
    class BaseCommitmentFormSet(BaseFormSet):
        def get_form_kwargs(self, index):
            kwargs = super(BaseCommitmentFormSet, self).get_form_kwargs(index)
            kwargs['proposal'] = proposals[index]
            kwargs['summary'] = summaries[index]
            kwargs['candidate'] = candidate
            return kwargs

        def save(self):
            for f in self.forms:
                f.save()

    num_forms = len(proposals)
    return formset_factory(SimpleCommitmentForm,
                           formset=BaseCommitmentFormSet,
                           max_num=num_forms,
                           min_num=num_forms, )