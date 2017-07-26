
from django.conf.urls import url
from votita.views import VotitaWizard

urlpatterns = [
    url(r'^crear/$',
        VotitaWizard.as_view(),
        name='create_proposal'),
]
