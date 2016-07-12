from django.conf.urls import patterns, url
from backend_citizen.views import (IndexView,
                                   PopularProposalTemporaryDataUpdateView,
                                   UpdateUserView,
                                   OrganizationDetailView,
                                   )

urlpatterns = patterns('',
                       url(r'^$',
                           IndexView.as_view(),
                           name='index'),
                       url(r'^organization/(?P<slug>[-\w]+)/?$',
                           OrganizationDetailView.as_view(),
                           name='organization'),
                       url(r'^update/?$',
                           UpdateUserView.as_view(),
                           name='update_my_profile'),
                       url(r'^update_temporary_data/(?P<pk>[\d]+)/?$',
                           PopularProposalTemporaryDataUpdateView.as_view(),
                           name='temporary_data_update'),
                       )
