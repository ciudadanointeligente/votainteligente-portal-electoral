
from django.conf.urls import url, include
from .views import (LoginView,
                    CPFAndDDNSelectView,
                    complete,
                    auth
                    )


urlpatterns = [
    url(r'^login/?$',
        LoginView.as_view(),
        name='candidate_login'),
    
    url(r'^cpf_e_ddn/?$',
        CPFAndDDNSelectView.as_view(),
        name='cpf_and_date'),
    url(r'^complete/(?P<backend>[^/]+)$',
        complete,
        name='candidate_social_complete'
        ),
    url(r'^login/(?P<backend>[^/]+)/?$', auth,
            name='candidato_social_begin'),
    
]
