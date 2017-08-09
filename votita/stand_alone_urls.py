
from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('votita.urls', namespace='votita')),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
]
