
from django.conf.urls import patterns, url
from backend_staff.views import IndexView

urlpatterns = patterns('',
    url(r'^index/?$',
        IndexView.as_view(),
        name='index'),
)
