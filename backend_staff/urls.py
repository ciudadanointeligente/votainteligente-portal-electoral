
from django.conf.urls import patterns, url
from backend_staff.views import (
    IndexView,
    PopularProposalCommentsView,
    ModeratePopularProposalView,
    AcceptPopularProposalView,
    RejectPopularProposalView,
)

urlpatterns = patterns('',
    url(r'^index/?$',
        IndexView.as_view(),
        name='index'),
    url(r'^popular_proposal_comments/(?P<pk>[-\w]+)/?$',
        PopularProposalCommentsView.as_view(),
        name='popular_proposal_comments'),
    url(r'^moderate_popular_proposal/(?P<pk>[-\w]+)/?$',
        ModeratePopularProposalView.as_view(),
        name='moderate_proposal'),
    url(r'^accept_popular_proposal/(?P<pk>[-\w]+)/?$',
        AcceptPopularProposalView.as_view(),
        name='accept_proposal'),
    url(r'^reject_popular_proposal/(?P<pk>[-\w]+)/?$',
        RejectPopularProposalView.as_view(),
        name='reject_proposal'),
)
