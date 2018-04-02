
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from merepresenta.forms import MeRepresentaMeiaLaranjaWizardForm
from elections.views import CandidateDetailView
from merepresenta.models import MeRepresentaCandidate


urlpatterns = [
    url(r'^$',
        TemplateView.as_view(template_name="merepresenta/index.html"),
        name='index'),
    url(r'^perguntas/?$',
        MeRepresentaMeiaLaranjaWizardForm.as_view(),
        name='questionary'),
    url(r'^eleccion/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/?$',
        CandidateDetailView.as_view(template_name='merepresenta/candidate_detail.html', model=MeRepresentaCandidate),
        name='candidate_detail_view'
        ),
]