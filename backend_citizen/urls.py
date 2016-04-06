from django.conf.urls import patterns, url
from backend_citizen.views import IndexView, PopularProposalTemporaryDataUpdateView

urlpatterns = patterns('',
    url(r'^index/?$',
        IndexView.as_view(),
        name='index'),
    url(r'^update_temporary_data/(?P<pk>[\d]+)/?$',
        PopularProposalTemporaryDataUpdateView.as_view(),
        name='temporary_data_update'),
)
