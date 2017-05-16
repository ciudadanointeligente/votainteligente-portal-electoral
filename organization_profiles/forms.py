# coding=utf-8
from django import forms
from organization_profiles.models import OrganizationTemplate, BASIC_FIELDS


class OrganizationTemplateForm(forms.ModelForm):
    class Meta:
        model = OrganizationTemplate
        fields = BASIC_FIELDS
