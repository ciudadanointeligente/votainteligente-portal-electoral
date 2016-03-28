
from django.conf.urls import patterns, url
from backend_staff.views import IndexView, PopularProposalCommentsView

urlpatterns = patterns('',
    url(r'^index/?$',
        IndexView.as_view(),
        name='index'),
    url(r'^popular_proposal_comments/(?P<pk>[-\w]+)/?$',
        PopularProposalCommentsView.as_view(),
        name='popular_proposal_comments'),
)
