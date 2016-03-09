from django.conf import settings
from django.conf.urls import patterns, url
from preguntales.views import (
    MessageDetailView,
    ElectionAskCreateView,
    AnswerWebHook,
    QuestionsPerCandidateView,
    ElectionRankingView,
    ConfirmationView,
)
from django.views.decorators.cache import cache_page

new_answer_endpoint = r"^new_answer/%s/?$" % (settings.NEW_ANSWER_ENDPOINT)

urlpatterns = patterns('',
    url(new_answer_endpoint,AnswerWebHook.as_view(), name='new_answer_endpoint' ),
    url(r'^election/(?P<election_slug>[-\w]+)/messages/(?P<pk>\d+)/?$',
        MessageDetailView.as_view(template_name='elections/message_detail.html'),
        name='message_detail'),
    url(r'^election/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/questions?$',
        QuestionsPerCandidateView.as_view(template_name='elections/questions_per_candidate.html'),
        name='questions_per_candidate'
        ),
    #ask
    url(r'^election/(?P<slug>[-\w]+)/ask/?$',
        ElectionAskCreateView.as_view(template_name='elections/ask_candidate.html'),
        name='ask_detail_view'),
    #ranking
    url(r'^election/(?P<slug>[-\w]+)/ranking/?$',
        cache_page(60 * settings.CACHE_MINUTES)(ElectionRankingView.as_view(template_name='elections/ranking_candidates.html')),
        name='ranking_view'),
    #confirmation
    url(r'^confirmation/(?P<key>[-\w]+)/?$',
        ConfirmationView.as_view(),
        name='confirmation'),
)
