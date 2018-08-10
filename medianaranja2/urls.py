from django.conf.urls import url
from medianaranja2.forms import MediaNaranjaOnlyProposals, MediaNaranjaWizardForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from constance import config
from medianaranja2.views import ShareYourResult, ShareMyResultPlz,ShareMyResultOrgPlz, SharedResultOGImageView





def get_medianaranja_view():
    if settings.MEDIA_NARANJA_QUESTIONS_ENABLED:
        view = MediaNaranjaWizardForm.as_view()
    else:
        view = MediaNaranjaOnlyProposals.as_view()

    try:
        if config.PRUEBAS_DE_CARGA_MEDIA_NARANJA:
            view = csrf_exempt(view)
    except:
        pass
    return view


urlpatterns = [
    url(r'^$',
        get_medianaranja_view(),
        name='index'),
    url(r'^simple$',
        MediaNaranjaOnlyProposals.as_view(),
        name='index_simple'),
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
