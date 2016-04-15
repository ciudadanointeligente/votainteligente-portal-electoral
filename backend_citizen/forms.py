from django import forms
from popolo.models import Organization
from backend_citizen.models import Enrollment


class OrganizationForm(forms.ModelForm):
    facebook_page = forms.URLField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(OrganizationForm, self).__init__(*args, **kwargs)

    def save(self, force_insert=False, force_update=False, commit=True):
        organization = super(OrganizationForm, self).save()
        Enrollment.objects.create(organization=organization,
                                  user=self.user)
        return organization

    class Meta:
        model = Organization
        fields = ['name', 'facebook_page']
