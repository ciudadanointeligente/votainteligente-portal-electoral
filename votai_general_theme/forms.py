# coding=utf-8
from django import forms


class PersonalDataForm(forms.Form):
    age = forms.IntegerField(label='Edad', required=False, initial=0)
    lema = forms.CharField(label=u'Lema de campaña', required=False, initial='')
    partido = forms.CharField(label=u'Partido', required=False, initial='')
    pacto = forms.CharField(label=u'Pacto', required=False, initial='')
    ocupacion = forms.CharField(label=u'Ocupación', required=False, initial='')
    experiencia = forms.CharField(label=u'Reseña Biográfica',
                                  widget=forms.Textarea(),
                                  max_length=4096,
                                  required=False,
                                  initial=''
                                  )
    telefono = forms.CharField(label=u'Teléfono',
                               required=False,
                               initial='',
                               help_text=u"¿Hay algún teléfono donde los ciudadanos interesados en tu campaña se puedan comunicar con tu comando?")
