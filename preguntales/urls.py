from django.conf import settings
from django.conf.urls import patterns, url
from preguntales.views import MessageDetailView, ElectionAskCreateView, AnswerWebHook, QuestionsPerCandidateView
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
)
