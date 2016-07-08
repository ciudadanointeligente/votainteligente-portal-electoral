
from django.conf.urls import patterns, url
from backend_candidate.views import (HomeView, )


urlpatterns = patterns('',
    url(r'^$',
        HomeView.as_view(),
        name='home'),
)
