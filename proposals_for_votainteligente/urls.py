from django.conf.urls import url
from popular_proposal.urls import urlpatterns
from proposals_for_votainteligente.views import (WithinAreaProposalCreationView,
                                                 CommitView,
                                                 NotCommitView,
                                                 ProposalsPerArea,
                                                 ThanksForProposingView,
                                                 ProposalWizardDependingOnArea,
                                                 ProposalWizardFull,
                                                 ProposalWizardFullWithoutArea,)
from django.views.decorators.clickjacking import xframe_options_exempt


urlpatterns += [
    url(r'^crear/?$',
        ProposalWizardFullWithoutArea.as_view(),
        name='propose_wizard_full_without_area'),
    url(r'^create_wizard/(?P<slug>[-\w]+)/?$',
        ProposalWizardDependingOnArea.as_view(),
        name='propose_wizard'),
    url(r'^create_wizard_full/?$',
        ProposalWizardFull.as_view(),
        name='propose_wizard_full'),
    url(r'^(?P<slug>[-\w]+)/?$',
        WithinAreaProposalCreationView.as_view(),
        name='propose'),
    url(r'^(?P<pk>[-\w]+)/gracias/?$',
        ThanksForProposingView.as_view(),
        name='thanks'),
    url(r'^commit/(?P<candidate_pk>[-\w]+)/(?P<proposal_pk>\d+)/?$',
        CommitView.as_view(),
        name='commit_yes'),
    url(r'^not_commit/(?P<candidate_pk>[-\w]+)/(?P<proposal_pk>\d+)/?$',
        NotCommitView.as_view(),
        name='commit_no'),
    url(r'^area_embedded/(?P<slug>[-\w]+)/?$',
        xframe_options_exempt(ProposalsPerArea.as_view(is_embedded=True)),
        name='area_embedded'),

]

