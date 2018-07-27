
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from merepresenta.forms import (MeRepresentaMeiaLaranjaWizardForm,
                                MeRepresentaMeiaLaranjaQuestionsWizardForm)
from elections.views import CandidateDetailView
from elections.models import QuestionCategory
from django.contrib import admin
from backend_candidate.views import CompleteMediaNaranjaView
from backend_candidate.forms import MediaNaranjaElectionForm
from merepresenta.voluntarios.views import (VolunteerIndexView,
                                            VolunteerLoginView,
                                            AddMailToCandidateView,
                                            ObrigadoView,
                                            auth,
                                            CouldNotFindCandidate,
                                            FacebookContacted,
                                            complete)

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
    url(r'^candidatos/?', include('backend_candidate.urls', namespace='backend_candidate')),
    url(r'^accounts/?', include('registration.backends.hmac.urls')),
    url(r'^voluntarios/?$',
        VolunteerIndexView.as_view(),
        name='volunteer_index'),
    url(r'^voluntarios/login/?$',
        VolunteerLoginView.as_view(),
        name='volunteer_login'),
    url(r'^login/(?P<backend>[^/]+)/?$', auth,
            name='voluntarios_social_begin'),
    url(r'^voluntarios/complete/(?P<backend>[^/]+)$',
        complete,
        name='volunteer_social_complete'
        ),
    url(r'^voluntarios/adicionar_mail/(?P<slug>[^/]+)$',
        AddMailToCandidateView.as_view(),
        name='add_mail_to_candidate'
        ),
    url(r'^voluntarios/obrigado/?$',
        ObrigadoView.as_view(),
        name='obrigado'
        ),
    url(r'^voluntarios/could_not_find_candidate/(?P<slug>[^/]+)$',
        CouldNotFindCandidate.as_view(),
        name='could_not_find_candidate'
        ),
    url(r'^voluntarios/facebook_contacted/(?P<slug>[^/]+)$',
        FacebookContacted.as_view(),
        name='facebook_contacted'
        ),
    # url('', include('social_django.urls', namespace='social'))add_mail_to_candidate
]
