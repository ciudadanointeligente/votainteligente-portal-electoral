# Create your views here.
from django.views.generic.edit import FormView
from elections.forms import ElectionSearchByTagsForm
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, DetailView, TemplateView
from elections.models import Election, VotaInteligenteMessage
from elections.forms import MessageForm
from candideitorg.models import Candidate
from writeit.models import Message

class ElectionsSearchByTagView(FormView):
    form_class = ElectionSearchByTagsForm
    template_name = 'search/tags_search.html'

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def form_valid(self, form):
        search_result = form.get_search_result()
        context = self.get_context_data(form=form, result=search_result)
        return self.render_to_response(context)


    def get_form_kwargs(self):
        kwargs = super(ElectionsSearchByTagView, self).get_form_kwargs()

        kwargs.update({
            'data': self.request.GET
        })
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(ElectionsSearchByTagView, self).get_context_data(**kwargs)
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse('tags_search')

class HomeView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['form'] = ElectionSearchByTagsForm()
        context['featured_elections'] = Election.objects.filter(highlighted = True)
        context['searchable_elections_enabled'] = True
        if Election.objects.filter(searchable = True) < 1:
            context['searchable_elections_enabled'] = False
        return context

class ElectionDetailView(DetailView):
    model = Election

    def get_context_data(self, **kwargs):
        context = super(ElectionDetailView, self).get_context_data(**kwargs)
        if self.object.can_election and 'slug_candidate_one' in self.kwargs:
            context['first_candidate'] = self.object.can_election.candidate_set.get(slug=self.kwargs['slug_candidate_one'])
        if self.object.can_election and 'slug_candidate_two' in self.kwargs:
            context['second_candidate'] = self.object.can_election.candidate_set.get(slug=self.kwargs['slug_candidate_two'])
        return context

class CandidateDetailView(DetailView):
    model = Candidate

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        #I know this is weird but this is basically
        #me the candidate.candideitorg_election.votainteligente_election
        #so that's why it says election.election
        context['election'] = self.object.election.election
        return context
        
class ElectionAskCreateView(CreateView):
    model = Message
    form_class = MessageForm

    def get_context_data(self, **kwargs):
        context = super(ElectionAskCreateView, self).get_context_data(**kwargs)
        election_slug = self.kwargs['slug']
        context['election'] = Election.objects.get(slug = election_slug)
        context['writeitmessages'] = VotaInteligenteMessage.objects.filter(writeitinstance=context['election'].writeitinstance)
        return context

    def get_form_kwargs(self):
        kwargs = super(ElectionAskCreateView, self).get_form_kwargs()
        election_slug = self.kwargs['slug']
        kwargs['writeitinstance'] = Election.objects.get(slug = election_slug).writeitinstance 
        return kwargs

    def get_success_url(self):
        election_slug = self.kwargs['slug']
        return reverse('ask_detail_view', kwargs={'slug':election_slug,})

from django.template.response import TemplateResponse
import requests, simplejson as json
from django.conf import settings

class SoulMateDetailView(DetailView):
    model = Election

    def post(self, request, *args, **kwargs):
        self.template_name = "elections/soulmate_response.html"
        election = super(SoulMateDetailView, self).get_object(self.get_queryset())
        self.object = election
        context = self.get_context_data()
        election_id = election.can_election.remote_id
        payload = {
            'data' : request.POST,
            "election-id":election_id
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(settings.CANDIDEITORG_URL + 'medianaranja/', data=json.dumps(payload), headers=headers)
        result = json.loads(response.content)

        winner_candidate = election.can_election.candidate_set.get(remote_id=result['winner']['candidate'])
        result["winner"]["candidate"] = winner_candidate
        context['winner'] = result["winner"]

        others_candidates=[]
        for other in result['others']:
            other_candidate = election.can_election.candidate_set.get(remote_id=other['candidate'])
            other["candidate"] = other_candidate
            others_candidates.append(other)

        context['others'] = others_candidates
        return self.render_to_response(context)