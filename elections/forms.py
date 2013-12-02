# coding=utf-8
from haystack.forms import SearchForm
from django import forms
from django.forms import ModelForm, CheckboxSelectMultiple
from django.utils.translation import ugettext as _
from elections.models import Election, VotaInteligenteMessage

class ElectionForm(SearchForm):
    pass

class ElectionSearchByTagsForm(forms.Form):
    q = forms.CharField(required=False, label=_('Busca tu comuna'))

    def get_search_result(self):
        cleaned_data = self.clean()
        queryed_element = cleaned_data['q']
        return Election.objects.filter(tags__name__in=[queryed_element])


class MessageForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.election = kwargs.pop('election')
        self.writeitinstance = self.election.writeitinstance
        super(MessageForm, self).__init__(*args, **kwargs)
        self.instance.writeitinstance = self.writeitinstance
        self.instance.api_instance = self.writeitinstance.api_instance
        self.fields['people'].queryset = self.election.popit_api_instance.person_set.filter(relation__reachable=True)

    class Meta:
        model = VotaInteligenteMessage
        fields = ('author_name', 'author_email', 'subject', 'content','people')
        widgets = {
            'people': CheckboxSelectMultiple(),
        }
        labels = {
            'author_name': _('Nombre'),
            'author_email': _(u'Correo electrónico'),
            'subject': _('Asunto'),
            'content': _('texto'),
            'people': _('Destinatarios'),
        }
        help_texts = {
            'people': _(u'Puedes seleccinar a más de un candidato para dirigir tu pregunta'),
            'author_name': _(u'Identíficate de alguna forma: Estudiante, Obrero, Democrático, Dirigente, etc.'),
        }
        error_messages = {
            'name': {
                'required': _('Debes identificarte de alguna forma.'),
            },
        }