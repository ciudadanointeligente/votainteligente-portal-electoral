# coding=utf-8
from django import forms
from votainteligente.facebook_page_getter import facebook_getter
from images.models import Image
from django.core.files.base import ContentFile
import requests
from django.utils.translation import ugettext as _
from popolo.models import ContactDetail
from backend_citizen.models import Profile
from django.contrib.auth.models import User
from registration.forms import RegistrationForm as UserCreationForm

try:
    import urlparse
    from urllib import urlencode
except: # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode


class UserChangeForm(forms.ModelForm):
    is_organization = forms.BooleanField(label=_(u"¿Eres una organización?"),
                                         required=False)
    image = forms.ImageField(required=False,
                             label=_(u"Imagen de perfil"))
    description = forms.CharField(widget=forms.Textarea,
                                  required=False,
                                  label=_(u"Descripción"))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'image', 'description']
        labels = {'first_name': _('Tu nombre'),
                  'last_name': _('Tu Apellido'),
                  }
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        for field in Profile._meta.fields:
            if field.name in self.fields.keys():
                self.initial[field.name] = getattr(self.instance.profile, field.name)

    def save(self):
        user = super(UserChangeForm, self).save()
        for key in self.cleaned_data:
            value = self.cleaned_data[key]
            if hasattr(user.profile, key):
                setattr(user.profile, key, value)
        user.profile.save()
        return user


class UserCreationForm(UserCreationForm):
    is_organization = forms.BooleanField(label=_(u'¿Eres una organización?'))

    class Meta:
        model = User
        fields = ('username', 'email', )

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=commit)
        user.profile.is_organization = self.cleaned_data['is_organization']
        if commit:
            user.profile.save()
        return user
