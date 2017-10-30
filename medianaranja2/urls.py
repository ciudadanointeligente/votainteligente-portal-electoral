from django.conf.urls import url
from medianaranja2.forms import MediaNaranjaWizardForm
from django.conf import settings

urlpatterns = [
    url(r'^$',
        MediaNaranjaWizardForm.as_view(),
        name='index'),
]
if settings.DEBUG:# pragma: no cover
    from medianaranja2.forms import MediaNaranjaResultONLYFORDEBUG
    urlpatterns += [
        url(r'^medianaranja2_resultado/$', MediaNaranjaResultONLYFORDEBUG.as_view(),
        name='medianaranja2_resultado')
    ]