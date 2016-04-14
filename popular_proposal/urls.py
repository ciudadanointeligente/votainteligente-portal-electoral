from django.conf.urls import patterns, url
from popular_proposal.views import (ProposalCreationView,
                                    ThanksForProposingView,
                                    SubscriptionView,
                                    HomeView,
                                    )

urlpatterns = patterns('',
    url(r'^/?$',
        HomeView.as_view(),
        name='home'),
    url(r'^(?P<slug>[-\w]+)/?$',
        ProposalCreationView.as_view(),
        name='propose'),
    url(r'^(?P<pk>[-\w]+)/gracias/?$',
        ThanksForProposingView.as_view(),
        name='thanks'),
    url(r'^(?P<pk>[-\w]+)/subscribe/?$',
        SubscriptionView.as_view(),
        name='like_a_proposal'),
)
