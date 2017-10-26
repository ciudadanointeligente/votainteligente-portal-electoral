from django.conf.urls import url
from medianaranja2.forms import MediaNaranjaWizardForm

urlpatterns = [
    url(r'^$',
        MediaNaranjaWizardForm.as_view(),
        name='index'),
]
