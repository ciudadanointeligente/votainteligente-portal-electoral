
from django.conf.urls import url
from votita.views import (VotitaWizard,
                          CreateGatheringView,
                          CreateProposalsForGathering,)
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^/?$', TemplateView.as_view(template_name="votita/index.html"),
                                      name='index'),
    url(r'^crear/?$',
        VotitaWizard.as_view(),
        name='create_proposal'),
    url(r'^crear_propuestas/(?P<pk>\d+)/?$',
        CreateProposalsForGathering.as_view(),
        name='proposal_for_gathering'),
    url(r'^crear_propuestas_wizard/(?P<pk>\d+)/?$',
        VotitaWizard.as_view(),
        name='create_proposal_for_gathering_wizard'),
    url(r'^crear_encuentro/?$',
        CreateGatheringView.as_view(),
        name='create_gathering'),

]
