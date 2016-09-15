# coding=utf-8
from django import forms
from django.utils.translation import ugettext as _
from backend_citizen.models import (Profile,
                                    Organization,
                                    Enrollment)
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

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=commit)
        if commit:
            user.profile.save()
        return user


class GroupCreationForm(UserCreationForm):
    name = forms.CharField(label=_(u'El nombre de tu organización'), max_length=30)

    class Meta:
        model = User
        fields = ('name', 'username', 'email', )
        labels = {'name': _(u'El nombre de tu organización'),
                  'username': _(u'Nombre de usuario, ej: amigosdelparque'),
                  'email': _(u'Email de la organización')
                  }

    def save(self, commit=True):
        group = super(GroupCreationForm, self).save(commit)
        group.first_name = self.cleaned_data['name']
        if commit:
            self.set_group_profile(group)
        return group

    def set_group_profile(self, group):
        group.save()
        group.profile.is_organization = True
        group.profile.save()
        return group


class OrganizationCreationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ('name', 'description')
        labels = {
            'name': _(u'¿Cuál es el nombre de tu grupo?'),
            'description': _(u'¿Podrías describirlo?'),
        }
        help_texts = {
            'name': _(u'Grupo de artistas callejeros.'),
            'description': _(u'Somos muy buena gente y nos gusta el arte.'),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(OrganizationCreationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        organization = super(OrganizationCreationForm, self).save(commit=commit)
        Enrollment.objects.create(user=self.user,
                                  organization=organization)
        return organization
