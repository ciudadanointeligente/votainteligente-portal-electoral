# coding=utf-8
from django import forms


class PersonalDataForm(forms.Form):
    age = forms.IntegerField(label='Edad', required=False)
    lema = forms.CharField(label=u'Lema de campaña', required=False)
    ocupacion = forms.CharField(label=u'Ocupación', required=False)
    experiencia = forms.CharField(label=u'Experiencia en Cargos públicos',
                                  widget=forms.Textarea(),
                                  max_length=4096,
                                  required=False
                                  )
