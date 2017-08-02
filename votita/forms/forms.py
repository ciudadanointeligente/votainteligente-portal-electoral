# coding=utf-8
from django import forms
from collections import OrderedDict
from popular_proposal.forms.forms import get_possible_generating_areas
from django.utils.translation import ugettext as _
from votita.models import KidsGathering
from django.forms import ModelForm


class CreateGatheringForm(ModelForm):
    class Meta:
        model = KidsGathering
        fields = ['name', 'presidents_features']


class UpdateGatheringForm(ModelForm):
    male = forms.IntegerField(min_value=0)
    female = forms.IntegerField(min_value=0)
    others = forms.IntegerField(min_value=0)
    class Meta:
        model = KidsGathering
        fields = ['image']

    def clean(self):
        cleaned_data = super(UpdateGatheringForm, self).clean()
        base_fields = [field.name for field in self._meta.model._meta.get_fields()]
        stats_data = {}
        for key  in cleaned_data.keys():
            if key not in base_fields:
                stats_data[key] = cleaned_data.pop(key)
        cleaned_data['stats_data'] = stats_data
        return cleaned_data

    def save(self):
        instance = super(UpdateGatheringForm, self).save(commit=False)
        instance.stats_data = self.cleaned_data['stats_data']
        instance.save()
        return instance

TOPIC_CHOICES = (('', u'Selecciona una categoría'),
                 ('asistencia', u'Asistencia y protección social'),
                 ('ciencias', u'Ciencias'),
                 ('cultura', u'Cultura'),
                 ('deporte', u'Deporte'),
                 ('derechoshumanos', u'Derechos Humanos'),
                 ('derechos', u'Derechos Sociales'),
                 ('emergencia', u'Desastres Naturales'),
                 ('economia', u'Economía'),
                 ('educacion', u'Educación'),
                 ('empleo', u'Empleo'),
                 ('energia', u'Energía'),
                 ('genero', u'Equidad y género'),
                 ('diversidad', u'Inclusión'),
                 ('infancia', u'Infancia y juventud'),
                 ('justicia', u'Justicia'),
                 ('medioambiente', u'Medio ambiente'),
                 ('medios', u'Medios de comunicación'),
                 ('migracion', u'Migración'),
                 ('mineria', u'Minería'),
                 ('pensiones', u'Pensiones'),
                 ('participacion', u'Participación'),
                 ('prevision', u'Previsión'),
                 ('proteccionsocial', u'Protección social'),
                 ('pueblosoriginarios', u'Pueblos originarios'),
                 ('recursosnaturales', u'Recursos naturales'),
                 ('salud', u'Salud'),
                 ('seguridad', u'Seguridad'),
                 ('sustentabilida', u'Sustentabilidad'),
                 ('terceraedad', u'Tercera Edad'),
                 ('trabajo', u'Trabajo'),
                 ('transparencia', u'Transparencia'),
                 ('transporte', u'Transporte'),
                 ('espaciospublicos', u'Urbanismo y Espacios públicos'),
                 )


wizard_forms_fields = [
    {
        'template': 'popular_proposal/wizard/paso1.html',
        'explation_template': "popular_proposal/steps/paso1.html",
        'fields': OrderedDict([(
            'clasification', forms.ChoiceField(choices=TOPIC_CHOICES,
                                               widget=forms.Select())
        ),
            ('problem', forms.CharField(max_length=1024,
                                        widget=forms.Textarea()
                                        ))
        ])
    },
    {
        'template': 'popular_proposal/wizard/paso5.html',
        'explation_template': "popular_proposal/steps/paso5.html",
        'fields': OrderedDict([
            ('title', forms.CharField(max_length=256,
                                      widget=forms.TextInput())),
            ('is_local_meeting', forms.BooleanField(required=False)),
            ('generated_at', forms.ModelChoiceField(required=False,
                                                    queryset=get_possible_generating_areas(),
                                                    empty_label="No aplica")
                                                    ),
            ('terms_and_conditions', forms.BooleanField(
                error_messages={'required':
                                _(u'Debes aceptar nuestros Términos y Condiciones')}
            )
            ),
        ])
    }
]
