from django.conf.urls import patterns, url
from popular_proposal.views import ProposalCreationView

urlpatterns = patterns('',
    url(r'^(?P<pk>[-\w]+)/?$',
        ProposalCreationView.as_view(),
        name='propose'),
)
