from django.conf.urls import url
from django.views.generic import TemplateView
from organization_profiles.views import OrganizationDetailView


urlpatterns = [
    url(r'^organization/(?P<slug>[-\w]+)/?$',
        OrganizationDetailView.as_view(),
        name='home'),
]
