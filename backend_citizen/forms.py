# coding=utf-8
from django import forms
from popular_proposal.models import Organization, Enrollment
from votainteligente.facebook_page_getter import facebook_getter
from images.models import Image
from django.core.files.base import ContentFile
import requests
from django.utils.translation import ugettext as _
from popolo.models import ContactDetail
try:
    import urlparse
    from urllib import urlencode
except: # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode


class OrganizationForm(forms.ModelForm):
    facebook_page = forms.URLField(required=False,
                                   label=_(u'¿Tienes una página en facebook?'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(OrganizationForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if Organization.objects.filter(name=name).exists():
            raise forms.ValidationError(_(u"Una organización con este nombre ya existe"), 'organization-exists')
        return name

    def clean_facebook_page(self):
        url = self.cleaned_data['facebook_page']
        url_parts = list(urlparse.urlparse(url))
        query = dict()
        url_parts[4] = urlencode(query)
        url = urlparse.urlunparse(url_parts)
        if url.endswith('/'):
            url = url[:-1]
        if ContactDetail.objects.filter(contact_type=ContactDetail.CONTACT_TYPES.facebook,
                                         value=url):
            raise forms.ValidationError(_(u"Una organización con esta página de Facebook ya existe"),
                                        'organization-facebook-exists')
        return url

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
