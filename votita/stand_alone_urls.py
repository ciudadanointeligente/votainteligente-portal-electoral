
from django.conf.urls import url, include
from votita.rest_api_router import router

urlpatterns = [
    url(r'^', include('votita.urls', namespace='votita')),
    url(r'^api/', include(router.urls)),
    url(r'^accounts/', include('votita.urls.registration_urls')),
    url(r'^', include('votainteligente.urls')),

]