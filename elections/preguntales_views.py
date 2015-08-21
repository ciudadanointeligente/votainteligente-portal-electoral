# coding=utf-8
from django.views.generic import DetailView, CreateView
from elections.models import VotaInteligenteMessage, Election
from elections.preguntales_forms import MessageForm
from django.core.urlresolvers import reverse
    

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

    def dispatch(self, *args, **kwargs):
        if 'slug' in kwargs:
            self.election = Election.objects.get(slug = kwargs['slug'])
        return super(ElectionAskCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ElectionAskCreateView, self).get_context_data(**kwargs)
        context['election'] = self.election
        context['writeitmessages'] = VotaInteligenteMessage.objects.filter(election=self.election)
        return context

    def get_form_kwargs(self):
        kwargs = super(ElectionAskCreateView, self).get_form_kwargs()
        election_slug = self.kwargs['slug']
        election = Election.objects.get(slug = election_slug)
        kwargs['election'] = election
        return kwargs

    def form_valid(self, form):
        form.instance.election = self.election
        return super(ElectionAskCreateView, self).form_valid(form)

    def get_success_url(self):
        election_slug = self.kwargs['slug']
        return reverse('ask_detail_view', kwargs={'slug':election_slug,})
