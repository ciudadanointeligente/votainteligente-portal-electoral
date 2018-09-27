from django.conf.urls import include, url
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^interes_candidato/$',
        TemplateView.as_view(template_name='registro_interes_candidato.html'),
        name='interes_candidato'),
] 
