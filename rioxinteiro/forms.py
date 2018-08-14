# coding=utf-8
from django import forms


class PersonalDataForm(forms.Form):
    lema = forms.CharField(label=u'Slogan da campanha', required=False, initial='')
    ocupacion = forms.CharField(label=u'Ocupação atual', required=False, initial='')
    raca = forms.CharField(label=u'Raça', required=False, initial='')
    orietacion_sexual = forms.CharField(label=u'Orientação sexual', required=False, initial='')
    territorio = forms.CharField(label=u'Território', required=False, initial='')
    experiencia = forms.CharField(label=u'Bio',
                                  widget=forms.Textarea(),
                                  max_length=4096,
                                  required=False,
                                  initial=''
                                  )
    telefono = forms.CharField(label=u'Número de telefone',
                               required=False,
                               initial='',
                               help_text=u"Existe um telefone onde os cidadãos interessados na sua campanha podem se comunicar com você?")
