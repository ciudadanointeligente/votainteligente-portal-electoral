from django.conf.urls import url
from medianaranja2.forms import MediaNaranjaWizardForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from constance import config
from medianaranja2.views import ShareYourResult, ShareMyResultPlz,ShareMyResultOrgPlz, SharedResultOGImageView

media_naranja2_view = MediaNaranjaWizardForm.as_view()

if config.PRUEBAS_DE_CARGA_MEDIA_NARANJA:
    media_naranja2_view = csrf_exempt(media_naranja2_view)

urlpatterns = [
    url(r'^$',
        media_naranja2_view,
        name='index'),
    url(r'^compartir/?$',
        ShareMyResultPlz.as_view(),
        name='create_share'),
    
    url(r'^compartir_org/?$',
        ShareMyResultOrgPlz.as_view(),
        name='create_share_org'),
    url(r'^compartir/(?P<identifier>[-\w]+)/?$',
        ShareYourResult.as_view(),
        name='share'),
    url(r'^og_image/(?P<identifier>[-\w]+).jpg$',
        SharedResultOGImageView.as_view(),
        name='og_image'),
]
if settings.DEBUG:# pragma: no cover
    from medianaranja2.forms import MediaNaranjaResultONLYFORDEBUG
    urlpatterns += [
        url(r'^medianaranja2_resultado/$', MediaNaranjaResultONLYFORDEBUG.as_view(),
        name='medianaranja2_resultado')
    ]