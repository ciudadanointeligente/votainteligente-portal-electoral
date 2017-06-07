# coding=utf-8
from django import forms
from organization_profiles.models import OrganizationTemplate, BASIC_FIELDS


class OrganizationTemplateForm(forms.ModelForm):
    title = forms.CharField(label="Nombre de tu organización",
                            widget=forms.TextInput(attrs={'placeholder': 'Fundación Ciudadano Inteligente'}))
    sub_title = forms.CharField(label="Nombre de tu organización",
                            widget=forms.Textarea(attrs={'placeholder': 'Ayúdanos a que te conozcan! En esta sección podrás contarnos sobre tu organización para informar a otros sobre tu labor social.'}))
    org_url = forms.URLField(label="Web de tu organización",
                             required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'https://miorganizacion.org'}))
    facebook = forms.URLField(label="FanPage de tu organización",
                              required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'https://www.facebook.com/miorganizacion/'}))
    twitter = forms.URLField(label="Twitter de tu organización",
                             required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'https://www.twitter.com/miorganizacion/'}))
    instagram = forms.URLField(label="Instagram de tu organización",
                               required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'https://www.instagram.com/miorganizacion/'}))
    rss_url = forms.URLField(label="RSS de tu organización",
                             required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'https://miorganizacion.org/rss.xml'}))

    primary_color = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '#CCDDCC',
                                                                  'type': 'color'}))
    secondary_color = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '#DDCCDD',
                                                                  'type': 'color'}))
    class Meta:
        model = OrganizationTemplate
        fields = BASIC_FIELDS
