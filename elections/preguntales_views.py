# coding=utf-8
from django.views.generic import DetailView
from elections.models import VotaInteligenteMessage, Election


class MessageDetailView(DetailView):
    model = VotaInteligenteMessage

    def get_context_data(self, **kwargs):
        context = super(MessageDetailView, self).get_context_data(**kwargs)
        election = Election.objects.get(slug=self.kwargs['election_slug'])
        context['election'] = election
        return context