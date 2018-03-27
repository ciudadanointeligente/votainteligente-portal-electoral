
from django.conf.urls import url, include
from votita.rest_api_router import router
from django.conf import settings


urlpatterns = [
    url(r'^', include('merepresenta.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
