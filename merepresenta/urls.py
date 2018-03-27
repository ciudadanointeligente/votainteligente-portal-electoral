
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from merepresenta.forms import MeRepresentaMeiaLaranjaWizardForm


urlpatterns = [
    url(r'^$',
        TemplateView.as_view(template_name="merepresenta/index.html"),
        name='index'),
    url(r'^perguntas/?$',
        MeRepresentaMeiaLaranjaWizardForm.as_view(),
        name='questionary'),
]