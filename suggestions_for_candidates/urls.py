
from django.conf.urls import url
from suggestions_for_candidates.views import (CandidateIncrementalDetailView,
                                     )
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    url(r'^commit_to_suggestions/(?P<identifier>[-\w]+)/?$',
        csrf_exempt(CandidateIncrementalDetailView.as_view()),
        name='commit_to_suggestions'),
]
