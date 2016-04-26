from django import forms
from popular_proposal.models import Organization, Enrollment
from votainteligente.facebook_page_getter import facebook_getter


class OrganizationForm(forms.ModelForm):
    facebook_page = forms.URLField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(OrganizationForm, self).__init__(*args, **kwargs)

    def save(self, force_insert=False, force_update=False, commit=True):
        organization = super(OrganizationForm, self).save()
        if 'facebook_page' in self.cleaned_data and self.cleaned_data['facebook_page']:
            result = facebook_getter(self.cleaned_data['facebook_page'])
            # organization.image = result['picture_url']
            organization.description = result['about']
            organization.save()
        Enrollment.objects.create(organization=organization,
                                  user=self.user)
        return organization

    class Meta:
        model = Organization
        fields = ['name', 'facebook_page']
