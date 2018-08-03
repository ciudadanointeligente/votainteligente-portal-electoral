
from django.conf.urls import url, include
from .views import (LoginView,
                    CPFAndDDNSelectView,
                    CPFAndDDNSelectView2,
                    CompleteProfileView,
                    complete,
                    auth
                    )


urlpatterns = [
    url(r'^login_after/?$',
        LoginView.as_view(),
        name='candidate_login'),
    
    url(r'^cpf_e_ddn/?$',
        CPFAndDDNSelectView.as_view(),
        name='cpf_and_date'),
    url(r'^login/?$',
        CPFAndDDNSelectView2.as_view(),
        name='cpf_and_date2'),
    url(r'^profile/(?P<slug>[-\w]+)/(?P<candidate_slug>[-\w]+)/?$',
        CompleteProfileView.as_view(),
        name='merepresenta_complete_profile'),
    url(r'^complete/(?P<backend>[^/]+)$',
        complete,
        name='candidate_social_complete'
        ),
    url(r'^login/(?P<backend>[^/]+)/(?P<slug>[^/]+)?$', auth,
            name='candidato_social_begin'),
    
]
