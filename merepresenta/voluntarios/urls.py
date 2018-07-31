
from django.conf.urls import url, include
from merepresenta.voluntarios.views import (VolunteerIndexView,
                                            VolunteerLoginView,
                                            AddMailToCandidateView,
                                            ObrigadoView,
                                            auth,
                                            CouldNotFindCandidate,
                                            FacebookContacted,
                                            UpdateAreaOfVolunteerView,
                                            complete)

urlpatterns = [
    url(r'^$',
        VolunteerIndexView.as_view(),
        name='volunteer_index'),
    url(r'^login/?$',
        VolunteerLoginView.as_view(),
        name='volunteer_login'),
    url(r'^login/(?P<backend>[^/]+)/?$', auth,
            name='voluntarios_social_begin'),
    url(r'^complete/(?P<backend>[^/]+)$',
        complete,
        name='volunteer_social_complete'
        ),
    url(r'^adicionar_mail/(?P<id>[^/]+)$',
        AddMailToCandidateView.as_view(),
        name='add_mail_to_candidate'
        ),
    url(r'^obrigado/?$',
        ObrigadoView.as_view(),
        name='obrigado'
        ),
    url(r'^could_not_find_candidate/(?P<id>[^/]+)$',
        CouldNotFindCandidate.as_view(),
        name='could_not_find_candidate'
        ),
    url(r'^facebook_contacted/(?P<id>[^/]+)$',
        FacebookContacted.as_view(),
        name='facebook_contacted'
        ),
    url(r'^update_area_of_volunteer$',
        UpdateAreaOfVolunteerView.as_view(),
        name='update_area_of_volunteer'
        ),
    
]
