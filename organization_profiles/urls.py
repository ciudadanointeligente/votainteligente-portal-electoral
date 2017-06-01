from django.conf.urls import url
from organization_profiles.views import OrganizationDetailView, OrganizationTemplateUpdateView


urlpatterns = [
    url(r'^update/extra_pages/(?P<pk>[-\w]+)/?$', OrganizationTemplateUpdateView.as_view(), name='update_extrapages'),
    url(r'^update/?$', OrganizationTemplateUpdateView.as_view(), name='update'),
    url(r'^(?P<slug>[-\w]+)/?$',
        OrganizationDetailView.as_view(),
        name='home'),
]
