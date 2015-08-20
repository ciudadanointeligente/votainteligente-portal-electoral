# coding=utf-8
from django.views.generic import DetailView, CreateView
from elections.models import VotaInteligenteMessage, Election
from elections.preguntales_forms import MessageForm

class MessageDetailView(DetailView):
    model = VotaInteligenteMessage

    def get_context_data(self, **kwargs):
        context = super(MessageDetailView, self).get_context_data(**kwargs)
        election = Election.objects.get(slug=self.kwargs['election_slug'])
        context['election'] = election
        return context


class ElectionAskCreateView(CreateView):
    model = VotaInteligenteMessage
    form_class = MessageForm

    def get_context_data(self, **kwargs):
        context = super(ElectionAskCreateView, self).get_context_data(**kwargs)
        election_slug = self.kwargs['slug']
        context['election'] = Election.objects.get(slug = election_slug)
        context['writeitmessages'] = VotaInteligenteMessage.objects.filter(election=context['election'])
        return context

    def get_form_kwargs(self):
        kwargs = super(ElectionAskCreateView, self).get_form_kwargs()
        election_slug = self.kwargs['slug']
        election = Election.objects.get(slug = election_slug)
        kwargs['election'] = election
        return kwargs

    def get_success_url(self):
        election_slug = self.kwargs['slug']
        return reverse('ask_detail_view', kwargs={'slug':election_slug,})
