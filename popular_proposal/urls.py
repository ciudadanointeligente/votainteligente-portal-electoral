from django.conf.urls import patterns, url
from popular_proposal.views import ProposalCreationView, ThanksForProposingView

urlpatterns = patterns('',
    url(r'^(?P<pk>[-\w]+)/?$',
        ProposalCreationView.as_view(),
        name='propose'),
    url(r'^(?P<pk>[-\w]+)/gracias/?$',
        ThanksForProposingView.as_view(),
        name='thanks'),
)
