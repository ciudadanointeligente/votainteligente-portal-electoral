
from django.conf.urls import patterns, url
from backend_candidate.views import (HomeView,
									 CompleteMediaNaranjaView,
									 CandidacyJoinView,
                                     CandidatePersonalDataUpdateView,
                                     )
from django.contrib.auth.views import login


urlpatterns = patterns('',
    url(r'^$',
        HomeView.as_view(),
        name='home'),
    url(r'^login/?$',
        login,
        {'template_name': 'backend_candidate/auth_login.html'},
        name='candidate_auth_login'),
    url(r'^media_naranja/(?P<slug>[-\w]+)/(?P<candidate_id>[-\w]+)/?$',
        CompleteMediaNaranjaView.as_view(),
        name='complete_12_naranja'),
    url(r'^complete_personal_data/(?P<slug>[-\w]+)/(?P<candidate_id>[-\w]+)/?$',
        CandidatePersonalDataUpdateView.as_view(),
        name='complete_personal_data'),
    url(r'^candidacy_user_join/(?P<identifier>[-\w]+)/?$',
        CandidacyJoinView.as_view(),
        name='candidacy_user_join'),

)
