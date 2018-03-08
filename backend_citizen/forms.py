# coding=utf-8
from django import forms
from django.utils.translation import ugettext as _
from backend_citizen.models import Profile
from django.contrib.auth.models import User
from registration.forms import RegistrationForm as UserCreationForm
try:
    import urlparse
    from urllib import urlencode
except:  # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode


class UserChangeForm(forms.ModelForm):
    image = forms.ImageField(required=False,
                             label=_(u"Imagen de perfil"))
    description = forms.CharField(widget=forms.Textarea,
                                  required=False,
                                  label=_(u"Descripción"))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'description']
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

    class Meta:
        model = User
        fields = ('username', 'email', )
        labels = {'username': _(u'Nombre de usuario, ej: votante1975, animal-mamifero, joven-idealista'),
                  'email': _(u'Email')
                  }
        help_texts = {'username': _(u'El nombre de usuario no tiene espacios ni acentos.')
                  }


    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=commit)
        if commit:
            user.profile.save()
        return user


class GroupCreationForm(UserCreationForm):
    name = forms.CharField(label=_(u'El nombre de tu organización'), max_length=30)

    class Meta:
        model = User
        fields = ('username', 'email', 'name', )
        labels = {'name': _(u'El nombre de tu organización'),
                  'username': _(u'Nombre de usuario, ej: amigosdelparque'),
                  'email': _(u'Email de la organización')
                  }

    def save(self, commit=True):
        group = super(GroupCreationForm, self).save(commit)

        group.last_name = self.cleaned_data['name']
        if commit:
            self.set_group_profile(group)
        return group

    def set_group_profile(self, group):
        group.save()
        group.profile.is_organization = True
        group.profile.save()
        return group