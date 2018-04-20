from django.conf.urls import url
from organization_profiles.views import (OrganizationDetailView,
                                         OrganizationTemplateUpdateView,
                                         AyuranosView,
                                         OrganizationListView,
                                         OrganizationTemplateOGPImage,
                                         ExtraPageUpdateView)


urlpatterns = [
    url(r'^$', OrganizationListView.as_view(), name='index'),
    url(r'^update/extra_pages/(?P<pk>[\d]+)/?$', ExtraPageUpdateView.as_view(), name='update_extrapage'),
    url(r'^update/?$', OrganizationTemplateUpdateView.as_view(), name='update'),
    url(r'^(?P<slug>[-\w]+)/?$',
        OrganizationDetailView.as_view(),
        name='home'),
    url(r'^(?P<slug>[-\w]+)/ayudanos/?$',
        AyuranosView.as_view(),
        name='ayuranos'),
    url(r'^og_image/(?P<slug>[-\w]+).jpg$',
        OrganizationTemplateOGPImage.as_view(),
        name='og_image'),
]
