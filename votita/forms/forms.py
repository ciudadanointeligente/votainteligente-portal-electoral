# coding=utf-8
from django import forms
from collections import OrderedDict
from proposals_for_votainteligente.forms import get_possible_generating_areas
from django.utils.translation import ugettext as _
from votita.models import KidsGathering, KidsProposal
from django.forms import ModelForm
from elections.models import Area
from votainteligente.send_mails import send_mails_to_staff
from django.conf import settings
from taggit.forms import TagWidget


def filterable_areas():
    areas = Area.public.all()
    if settings.FILTERABLE_AREAS_TYPE:
        return areas.filter(classification__in=settings.FILTERABLE_AREAS_TYPE)
    return areas


class GatheringsWithStatsDataMixin(object):
    def clean(self):
        cleaned_data = super(GatheringsWithStatsDataMixin, self).clean()
        base_fields = [field.name for field in self._meta.model._meta.get_fields()]
        stats_data = {}
        for key  in cleaned_data.keys():
            if key not in base_fields:
                stats_data[key] = cleaned_data.pop(key)
        cleaned_data['stats_data'] = stats_data
        return cleaned_data

    def save(self, commit=True):
        instance = super(GatheringsWithStatsDataMixin, self).save(commit=False)
        creating = instance.pk is None
        if creating:
            instance.proposer = self.proposer

        instance.stats_data = self.cleaned_data['stats_data']
        instance.save()
        if creating:
            self.save_m2m()
        return instance


AGE_CHOICES = (("", u"Selecciona un rango de etario"), ("basica", u"Educación Básica"),("media", u"Educación Media"),("otro", u"Otro"),)

class CreateGatheringForm(GatheringsWithStatsDataMixin, ModelForm):
    age_range = forms.ChoiceField(label= "Rango etario de los participantes",
                                  required=True,
                                  choices=AGE_CHOICES)
    male = forms.IntegerField(label = "Cantidad de Niños",
                              min_value = 0,
                              initial=0)
    female = forms.IntegerField(label = "Cantidad de Niñas",
                                min_value = 0,
                                initial=0)
    others = forms.IntegerField(label = "Cantidad de Otros",
                                min_value = 0,
                                initial=0)
    generated_at = forms.ModelChoiceField(queryset=filterable_areas(),
                                          empty_label=u"Selecciona la comuna",
                                          required=False,
                                          label="Comuna donde se realizó el encuentro")
    school = forms.CharField(required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Ejemplo: “Escuela Santa Isabel”'}),
                             label=u"Establecimiento u organización")

    class Meta:
        model = KidsGathering
        fields = ['name', 'generated_at', 'presidents_features', 'school']
        widgets = {
            "name" :forms.TextInput(attrs={'placeholder': 'Ejemplo: “Quinto básico C”'}),
            "presidents_features": TagWidget(attrs={"max_length":100})
        }

    def __init__(self, *args, **kwargs):
        self.proposer = kwargs.pop('proposer')
        super(CreateGatheringForm, self).__init__(*args, **kwargs)


class UpdateGatheringForm(GatheringsWithStatsDataMixin, ModelForm):
    class Meta:
        model = KidsGathering
        fields = ['image', 'comments']

    def save(self, commit=True):
        instance = super(UpdateGatheringForm, self).save(commit)
        send_mails_to_staff({'gathering': instance}, 'nuevo_encuentro_en_votita')
        return instance


TOPIC_CHOICES = (('', u'Selecciona el tema'),
                 ('proteccion_y_familia', u'Protección y familia'),
                 ('educacion_y_trabajo', u'Educación y trabajo'),
                 ('tecnologia', u'Tecnología y comunicaciones'),
                 ('diversidad', u'Diversidad e integración'),
                 ('cultura', u'Cultura y tiempo libre'),
                 ('medio_ambiente', u'Medio ambiente'),
                 ('salud', u'Salud y bienestar'),
                 ('politica', u'Política y participación'),
                 )
TOPIC_CHOICES_DICT = dict(TOPIC_CHOICES)

wizard_forms_fields = [
    {
        'template': 'popular_proposal/wizard/form_step.html',
        'explation_template': "popular_proposal/steps/tips_vacio.html",
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
        'explation_template': "popular_proposal/steps/tips_vacio.html",
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


class KidsProposalForm(ModelForm):
    solution = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Detalle de la propuesta'}))
    clasification = forms.ChoiceField(choices=TOPIC_CHOICES)

    class Meta:
        model = KidsProposal
        fields = ['title', 'clasification']
        widgets = {
            "title" : forms.TextInput(attrs={'placeholder': 'Título de la propuesta'})
        }

    def save(self, commit=True):
        instance = super(KidsProposalForm, self).save(commit=commit)
        instance.data = {
            'solution': self.cleaned_data['solution']
        }
        if commit:
            instance.save()
        return instance
