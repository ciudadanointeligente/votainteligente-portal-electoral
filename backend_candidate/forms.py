# coding=utf-8
from django import forms
from candidator.models import Topic, Position, TakenPosition
from collections import OrderedDict
from django.utils.translation import ugettext as _


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
    if taken_position:
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