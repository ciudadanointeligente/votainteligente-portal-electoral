from django.conf.urls import url
from popular_proposal.urls import urlpatterns
from proposals_for_votainteligente.views import (WithinAreaProposalCreationView,

                                                 ProposalsPerArea,
                                                 ThanksForProposingView)
from django.views.decorators.clickjacking import xframe_options_exempt


urlpatterns += [
    url(r'^(?P<slug>[-\w]+)/?$',
        WithinAreaProposalCreationView.as_view(),
        name='propose'),
    url(r'^(?P<pk>[-\w]+)/gracias/?$',
        ThanksForProposingView.as_view(),
        name='thanks'),
    url(r'^area_embedded/(?P<slug>[-\w]+)/?$',
        xframe_options_exempt(ProposalsPerArea.as_view(is_embedded=True)),
        name='area_embedded'),
]