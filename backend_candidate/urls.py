
from django.conf.urls import patterns, url
from backend_candidate.views import (HomeView,
                                     CompleteMediaNaranjaView,
                                     CandidacyJoinView,
                                     ProfileView,
                                     MyCommitments,
                                     ProposalsForMe,
                                     HelpFindingCandidates,
                                     )
from django.contrib.auth.views import login
from django.views.decorators.cache import cache_page
from django.conf import settings


urlpatterns = patterns('',
    url(r'^$',
        HomeView.as_view(),
        name='home'),
    url(r'^ayudanos/$',
        cache_page(60 * settings.HEAVY_PAGES_CACHE_MINUTES)(HelpFindingCandidates.as_view()),
        name='help'),
    url(r'^login/?$',
        login,
        {'template_name': 'backend_candidate/auth_login.html'},
        name='candidate_auth_login'),
    url(r'^profile/(?P<slug>[-\w]+)/(?P<candidate_id>[-\w]+)/?$',
        ProfileView.as_view(),
        name='complete_profile'),
    url(r'^media_naranja/(?P<slug>[-\w]+)/(?P<candidate_id>[-\w]+)/?$',
        CompleteMediaNaranjaView.as_view(),
        name='complete_12_naranja'),
    url(r'^my_commitments/(?P<slug>[-\w]+)/(?P<candidate_id>[-\w]+)/?$',
        MyCommitments.as_view(),
        name='my_proposals_with_a_resolution'),
    url(r'^proposals_for_me/(?P<slug>[-\w]+)/(?P<candidate_id>[-\w]+)/?$',
        ProposalsForMe.as_view(),
        name='proposals_for_me'),
    url(r'^candidacy_user_join/(?P<identifier>[-\w]+)/?$',
        CandidacyJoinView.as_view(),
        name='candidacy_user_join'),

)
