
from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('votita.urls', namespace='votita')),

    url(r'^cuentas/', include('votita.urls.auth_urls')),
    url(r'^accounts/', include('votita.urls.registration_urls')),
    url(r'^', include('votainteligente.urls')),

]
