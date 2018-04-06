
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from merepresenta.forms import (MeRepresentaMeiaLaranjaWizardForm,
                                MeRepresentaMeiaLaranjaQuestionsWizardForm)
from elections.views import CandidateDetailView
from elections.models import QuestionCategory
from django.contrib import admin
from backend_candidate.views import CompleteMediaNaranjaView
from backend_candidate.forms import MediaNaranjaElectionForm

class MeRepresentaMeiaLaranjaForm(MediaNaranjaElectionForm):
    def __init__(self, *args, **kwargs):
        self.categories  = QuestionCategory.objects.all()
        super(MeRepresentaMeiaLaranjaForm, self).__init__(*args, **kwargs)

class MeRepresentaMeiaLaranja(CompleteMediaNaranjaView):
    def get_form_class(self):
        return MeRepresentaMeiaLaranjaForm


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',
        TemplateView.as_view(template_name="merepresenta/index.html"),
        name='index'),
    url(r'^perguntas/?$',
        MeRepresentaMeiaLaranjaWizardForm.as_view(),
        name='questionary'),
    url(r'^answers/?$',
        MeRepresentaMeiaLaranjaQuestionsWizardForm.as_view(),
        name='questions'),
    url(r'^eleccion/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/?$',
        CandidateDetailView.as_view(template_name='merepresenta/candidate_detail.html'),
        name='candidate_detail_view'
        ),
    url(r'^candidatos/media_naranja/(?P<slug>[-\w]+)/(?P<candidate_slug>[-\w]+)/?$',
        MeRepresentaMeiaLaranja.as_view(),
        name='complete_12_naranja'),
    url(r'^candidatos/', include('backend_candidate.urls', namespace='backend_candidate')),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url('', include('social_django.urls', namespace='social'))
]
