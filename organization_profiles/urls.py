from django.conf.urls import url
from organization_profiles.views import OrganizationDetailView, OrganizationTemplateUpdateView
from django.views.generic.edit import UpdateView
from organization_profiles.models import ExtraPage


urlpatterns = [
    url(r'^update/extra_pages/(?P<pk>[\d]+)/?$', UpdateView.as_view(model=ExtraPage,
                                                                    fields=['title', 'content'],
                                                                    template_name="backend_organization/update_extrapage.html",
                                                                    ), name='update_extrapage'),
    url(r'^update/?$', OrganizationTemplateUpdateView.as_view(), name='update'),
    url(r'^(?P<slug>[-\w]+)/?$',
        OrganizationDetailView.as_view(),
        name='home'),
]
