
from django.conf.urls import url
from backend_candidate.views import (HomeView,
                                     CompleteMediaNaranjaView,
                                     CandidacyJoinView,
                                     ProfileView,
                                     MyCommitments,
                                     ProposalsForMe,
                                     HelpFindingCandidates,
                                     AddActivityToCandidateView,
                                     MyActivitiesListView,
                                     CandidateIncrementalDetailView,
                                     )
from django.contrib.auth.views import login
from django.views.generic.base import TemplateView
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    url(r'^$',
        HomeView.as_view(),
        name='home'),
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
    url(r'^add_activity/(?P<slug>[-\w]+)/?$',
        AddActivityToCandidateView.as_view(),
        name='add_activity'),
    url(r'^all_my_activities/(?P<slug>[-\w]+)/?$',
        MyActivitiesListView.as_view(),
        name='all_my_activities'),
    url(r'^commit_to_suggestions/(?P<identifier>[-\w]+)/?$',
        csrf_exempt(xframe_options_exempt(CandidateIncrementalDetailView.as_view())),
        name='commit_to_suggestions'),
    url(r'^gracias_totales/$',
        TemplateView.as_view(template_name='backend_candidate/thanks_for_commiting.html'),
        name='thanks_for_commiting'),
]
