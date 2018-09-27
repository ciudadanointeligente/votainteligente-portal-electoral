from django.conf.urls import url
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from medianaranja2.views import (ShareYourResult,
                                 ShareMyResultPlz,
                                 ShareMyResultOrgPlz,
                                 SharedResultOGImageView,
                                 get_medianaranja_view)
from django.utils.translation import ugettext_lazy as _


urlpatterns = [
    url(r'^$',
        get_medianaranja_view,
        name='index'),
    url(_(r'^compartir/?$'),
        ShareMyResultPlz.as_view(),
        name='create_share'),
    
    url(_(r'^compartir_org/?$'),
        ShareMyResultOrgPlz.as_view(),
        name='create_share_org'),
    url(_(r'^compartir/(?P<identifier>[-\w]+)/?$'),
        ShareYourResult.as_view(),
        name='share'),
    url(_(r'^og_image/(?P<identifier>[-\w]+).jpg$'),
        SharedResultOGImageView.as_view(),
        name='og_image'),
]
if settings.DEBUG:# pragma: no cover
    from medianaranja2.forms import MediaNaranjaResultONLYFORDEBUG
    urlpatterns += [
        url(r'^medianaranja2_resultado/$', MediaNaranjaResultONLYFORDEBUG.as_view(),
        name='medianaranja2_resultado')
    ]
