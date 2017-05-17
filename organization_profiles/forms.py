# coding=utf-8
from django import forms
from organization_profiles.models import OrganizationTemplate, BASIC_FIELDS


class OrganizationTemplateForm(forms.ModelForm):
    primary_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
    secondary_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
    class Meta:
        model = OrganizationTemplate
        fields = BASIC_FIELDS
