from django.conf.urls import patterns, url
from popular_proposal.views import (ProposalCreationView,
                                    ThanksForProposingView,
                                    SubscriptionView,)

urlpatterns = patterns('',
    url(r'^(?P<pk>[-\w]+)/?$',
        ProposalCreationView.as_view(),
        name='propose'),
    url(r'^(?P<pk>[-\w]+)/gracias/?$',
        ThanksForProposingView.as_view(),
        name='thanks'),
    url(r'^(?P<pk>[-\w]+)/subscribe/?$',
        SubscriptionView.as_view(),
        name='like_a_proposal'),
)
