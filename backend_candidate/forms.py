# coding=utf-8
from django import forms
from candidator.models import Topic, Position, TakenPosition
from collections import OrderedDict


def get_field_from_topic(topic):
    field = forms.ChoiceField(widget=forms.RadioSelect)
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

def get_fields_dict_from_topic(topic):
    dict_ = OrderedDict()
    topic_id = str(topic.id)
    dict_['topic_' + topic_id] = forms.IntegerField(widget=forms.HiddenInput,
                                                    initial=topic.id)
    dict_['answer_for_' + topic_id] = get_field_from_topic(topic)
    dict_['description_for_' + topic_id] = forms.CharField(widget=forms.TextInput)
    return dict_

def get_form_for_area(area):
    class MediaNaranjaAreaForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super(MediaNaranjaAreaForm, self).__init__(*args, **kwargs)
            for category in area.categories.all():
                for topic in category.topics.all():
                    self.fields.update(get_fields_dict_from_topic(topic))

    return MediaNaranjaAreaForm