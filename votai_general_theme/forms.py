# coding=utf-8
from django import forms


class PersonalDataForm(forms.Form):
    age = forms.IntegerField(label='Edad')
    lema = forms.CharField(label=u'Lema de campaña')
    ocupacion = forms.CharField(label=u'Ocupación')
    experiencia = forms.CharField(label=u'Experiencia en Cargos públicos',
                                  widget=forms.Textarea())
