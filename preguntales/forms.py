# coding=utf-8
from django.forms import ModelForm, CheckboxSelectMultiple
from preguntales.models import Message
from django.utils.translation import ugettext as _

class MessageForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.election = kwargs.pop('election')
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['people'].queryset = self.election.candidates.exclude(email__isnull=True).exclude(email__exact='')

    class Meta:
        model = Message
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
