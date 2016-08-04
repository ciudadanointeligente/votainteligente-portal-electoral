
from django.conf.urls import patterns, url
from backend_candidate.views import (HomeView,
									 CompleteMediaNaranjaView,
									 CandidacyJoinView)


urlpatterns = patterns('',
    url(r'^$',
        HomeView.as_view(),
        name='home'),
    url(r'^media_naranja/(?P<slug>[-\w]+)/(?P<candidate_id>[-\w]+)/?$',
        CompleteMediaNaranjaView.as_view(),
        name='complete_12_naranja'),
    url(r'^candidacy_user_join/(?P<identifier>[-\w]+)/?$',
        CandidacyJoinView.as_view(),
        name='candidacy_user_join'),

)
