
from django.conf.urls import patterns, url
from backend_candidate.views import (HomeView,
									 CompleteMediaNaranjaView,)


urlpatterns = patterns('',
    url(r'^$',
        HomeView.as_view(),
        name='home'),
    url(r'^media_naranja/(?P<slug>[-\w]+)/(?P<candidate_id>[-\w]+)/?$',
        CompleteMediaNaranjaView.as_view(),
        name='complete_12_naranja'),
)
