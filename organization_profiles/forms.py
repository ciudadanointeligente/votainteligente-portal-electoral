# coding=utf-8
from django import forms
from organization_profiles.models import OrganizationTemplate, BASIC_FIELDS
from django.utils.translation import ugettext_lazy as _


class OrganizationTemplateForm(forms.ModelForm):
    title = forms.CharField(label="Nombre de tu organización",
                            required=False,
                            widget=forms.TextInput(attrs={'placeholder': _(u'Organización Organizada')}))
    sub_title = forms.CharField(label="Nombre de tu organización",
                                required=False,
                                widget=forms.Textarea(attrs={'placeholder': _(u'Ayúdanos a que te conozcan! En esta sección podrás contarnos sobre tu organización para informar a otros sobre tu labor social.')}))
    org_url = forms.URLField(label="Web de tu organización",
                             required=False,
                            widget=forms.TextInput(attrs={'placeholder': _(u'https://miorganizacion.org')}))
    facebook = forms.URLField(label="FanPage de tu organización",
                              required=False,
                            widget=forms.TextInput(attrs={'placeholder': _(u'https://www.facebook.com/miorganizacion/')}))
    twitter = forms.URLField(label="Twitter de tu organización",
                             required=False,
                            widget=forms.TextInput(attrs={'placeholder': _(u'https://www.twitter.com/miorganizacion/')}))
    instagram = forms.URLField(label="Instagram de tu organización",
                               required=False,
                            widget=forms.TextInput(attrs={'placeholder': _(u'https://www.instagram.com/miorganizacion/')}))
    rss_url = forms.URLField(label="RSS de tu organización",
                             required=False,
                            widget=forms.TextInput(attrs={'placeholder': _(u'https://miorganizacion.org/rss.xml')}))

    primary_color = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '#CCDDCC',
                                                                  'type': 'color'}))
    secondary_color = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '#DDCCDD',
                                                                  'type': 'color'}))
    class Meta:
        model = OrganizationTemplate
        fields = BASIC_FIELDS
