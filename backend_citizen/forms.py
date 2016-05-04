# coding=utf-8
from django import forms
from popular_proposal.models import Organization, Enrollment
from votainteligente.facebook_page_getter import facebook_getter
from images.models import Image
from django.core.files.base import ContentFile
import requests
from django.utils.translation import ugettext as _
from popolo.models import ContactDetail


class OrganizationForm(forms.ModelForm):
    facebook_page = forms.URLField(required=False,
                                   label=_(u'¿Tienes una página en facebook?'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(OrganizationForm, self).__init__(*args, **kwargs)

    def save(self, force_insert=False, force_update=False, commit=True):
        organization = super(OrganizationForm, self).save()
        if 'facebook_page' in self.cleaned_data and self.cleaned_data['facebook_page']:
            result = facebook_getter(self.cleaned_data['facebook_page'])
            image_content = ContentFile(requests.get(result['picture_url']).content)

            image = Image.objects.create(content_object=organization, source=result['picture_url'])
            image.image.save(organization.id, image_content)
            organization.description = result['about']
            organization.save()
            c = ContactDetail(content_object=organization,
                              contact_type=ContactDetail.CONTACT_TYPES.facebook,
                              value=self.cleaned_data['facebook_page'],
                              label=result['name'])
            c.save()

        Enrollment.objects.create(organization=organization,
                                  user=self.user)
        return organization

    class Meta:
        model = Organization
        fields = ['name', 'facebook_page']
