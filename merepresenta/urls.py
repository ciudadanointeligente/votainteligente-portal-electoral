
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from merepresenta.forms import MeRepresentaMeiaLaranjaWizardForm
from elections.views import CandidateDetailView
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',
        TemplateView.as_view(template_name="merepresenta/index.html"),
        name='index'),
    url(r'^perguntas/?$',
        MeRepresentaMeiaLaranjaWizardForm.as_view(),
        name='questionary'),
    url(r'^eleccion/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/?$',
        CandidateDetailView.as_view(template_name='merepresenta/candidate_detail.html'),
        name='candidate_detail_view'
        ),
    url(r'^candidatos/', include('backend_candidate.urls', namespace='backend_candidate')),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url('', include('social_django.urls', namespace='social'))
]
