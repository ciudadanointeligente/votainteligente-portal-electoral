from django.conf.urls import url
from organization_profiles.views import OrganizationDetailView, OrganizationTemplateUpdateView


urlpatterns = [
    url(r'^update/?$', OrganizationTemplateUpdateView.as_view(), name='update'),
    url(r'^(?P<slug>[-\w]+)/?$',
        OrganizationDetailView.as_view(),
        name='home'),
]
