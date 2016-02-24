# coding=utf-8
from django.views.generic import DetailView, CreateView
from elections.models import VotaInteligenteMessage, Election, Candidate, VotaInteligenteAnswer
from preguntales.forms import MessageForm
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from elections.writeit_functions import reverse_person_url
from django.core.mail import mail_admins
from elections.views import CandidateDetailView
from django.db.models import Q


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


class AnswerWebHook(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AnswerWebHook, self).dispatch(request, *args, **kwargs)


    def post(self, *args, **kwargs):
        person_id = self.request.POST.get('person_id')
        content = self.request.POST.get('content')

        message_id = self.request.POST.get('message_id')
        try:
            message = VotaInteligenteMessage.objects.get(url=message_id)
            person_id = reverse_person_url(person_id)
            person = Candidate.objects.get(id=person_id)
            VotaInteligenteAnswer.objects.create(person =person, message=message, content=content)
        except Exception, e:
            mail_admins('Error recibiendo una respuesta', e)

        return HttpResponse(content_type="text/plain", status=200)

class QuestionsPerCandidateView(CandidateDetailView):
    def get_queryset(self):

        queryset = super(QuestionsPerCandidateView, self).get_queryset()
        election_slug = self.kwargs['election_slug']
        queryset.filter(Q(elections__slug=election_slug))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(QuestionsPerCandidateView, self)\
            .get_context_data(**kwargs)
        messages = VotaInteligenteMessage.objects.filter(people=self.object)
        context['questions'] = messages
        return context
