from django.conf.urls import url
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^organization/(?P<slug>[-\w]+)/?$',
        TemplateView.as_view(template_name='encuentroONGs.html'),
        name='home'),
]
