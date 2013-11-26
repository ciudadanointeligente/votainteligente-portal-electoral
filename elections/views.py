# coding=utf-8
from django.views.generic.edit import FormView
from elections.forms import ElectionSearchByTagsForm
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, DetailView, TemplateView
from elections.models import Election, VotaInteligenteMessage, VotaInteligenteAnswer
from elections.forms import MessageForm
from candideitorg.models import Candidate
from popit.models import Person
from writeit.models import Message
from django.views.generic.base import View
import logging
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from operator import itemgetter

logger = logging.getLogger(__name__)

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


class FaceToFaceView(ElectionDetailView):
    def get_context_data(self, **kwargs):
        context = super(FaceToFaceView, self).get_context_data(**kwargs)
        if 'first_candidate' in context and 'second_candidate' in context:
            candidate1, candidate2 = context['first_candidate'], context['second_candidate']
            categories = self.object.can_election.category_set.all()
            equal_answers = 0
            total_questions = 0
            for cat in categories:
              for question in cat.question_set.all():
                total_questions += 1
                try:
                  if candidate2.answers.get(question=question) == candidate1.answers.get(question=question):
                    equal_answers += 1
                except:
                  pass
            if total_questions:
                context['similitude'] = equal_answers*100/total_questions
            else:
                context['similitude'] = 0
        return context

class CandidateDetailView(DetailView):
    model = Candidate

    def get_queryset(self):
        queryset = super(CandidateDetailView, self).get_queryset()
        queryset = queryset.filter(election__slug=self.kwargs['election_slug'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        #I know this is weird but this is basically
        #me the candidate.candideitorg_election.votainteligente_election
        #so that's why it says election.election
        context['election'] = self.object.election.election
        return context


class QuestionsPerCandidateView(CandidateDetailView):
    def get_queryset(self):

        queryset = super(QuestionsPerCandidateView, self).get_queryset()
        election_slug = self.kwargs['election_slug']
        queryset.filter(Q(election__slug=election_slug))
        return queryset
        

    def get_context_data(self, **kwargs):
        context = super(QuestionsPerCandidateView, self).get_context_data(**kwargs)
        context['questions'] = VotaInteligenteMessage.objects.filter(people=self.object.relation.person)
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
from django.http import HttpResponse

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
            person = Person.objects.get(popit_url=person_id)
            VotaInteligenteAnswer.objects.create(person =person, message=message, content=content)
        except Exception, e:
            logger.error(e)

        response = HttpResponse(content_type="text/plain", status=200)
        return response

class RankingMixin(object):
    candidate_queryset = None
    votainteligentemessages = None

    def __init__(self, *args, **kwargs):
        super(RankingMixin, self).__init__(*args, **kwargs)
        

    def get_ranking(self):
        return self.candidate_queryset

    def all_messages(self):
        if not self.votainteligentemessages:
            self.votainteligentemessages = VotaInteligenteMessage.objects\
                    .filter(people__in=self.candidate_queryset)
        return self.votainteligentemessages

    def all_possible_answers(self):
        answers = self.all_messages()
        total_possible_answers=0
        for answer in answers:
            total_possible_answers += answer.people.count()

        return total_possible_answers


    def actual_answers(self):

        messages = self.all_messages()
        actual_count = 0
        for message in messages:
            actual_count += message.answers.count()
        return actual_count

    def success_index(self):
        return float(self.all_possible_answers())/float(self.actual_answers())


    def get_clasified(self):
        clasified = []
        messages = self.all_messages()
        if not messages:
            return []
        are_there_answers = VotaInteligenteAnswer.objects.filter(message__in=messages).exists()
        if not are_there_answers:
            return []
        success_index = self.success_index()
        for candidate in self.candidate_queryset:
            possible_answers = VotaInteligenteMessage.objects.filter(Q(people=candidate)).count()
            actual_answers = VotaInteligenteAnswer.objects.filter(Q(person=candidate) & Q(message__in=messages)).count()
            points = (success_index + 1)*possible_answers*actual_answers\
                                                         - possible_answers*possible_answers
            clasified.append({
                'id':candidate.id,
                'name':candidate.name,
                'candidate':candidate,
                'possible_answers':possible_answers,
                'actual_answers':actual_answers,
                'points':points
                })
        return clasified

    def get_ordered(self):
        clasified = self.get_clasified()
        clasified = sorted(clasified,  key=itemgetter('points'), reverse=True)

        return clasified


    def get_good(self):
        amount_of_good_ones = self.candidate_queryset.count()/2
        good = []
        ordered = self.get_ordered()
        for i in range(0, min(amount_of_good_ones, len(ordered))):
            if ordered[i]["actual_answers"] > 0:
                good.append(ordered[i])
        return good

    def get_bad(self):
        amount_of_bad_ones = -self.candidate_queryset.count()/2
        ordered = self.get_ordered()[::-1]
        bad = ordered[:amount_of_bad_ones]
        for item in ordered[amount_of_bad_ones:]:
            if item["actual_answers"] > 0:
                break
            bad.append(item)
        return bad


class ElectionRankingView(DetailView, RankingMixin):
    model = Election


    def get_object(self, queryset=None):
        the_object = super(ElectionRankingView, self).get_object(queryset)
        queryset = the_object.popit_api_instance.person_set.all()
        self.candidate_queryset = queryset
        return the_object


    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['good'] = self.get_good()
        context['bad'] = self.get_bad()
        return context


class MessageDetailView(DetailView):
    model = VotaInteligenteMessage

    def get_context_data(self, **kwargs):
        context = super(MessageDetailView, self).get_context_data(**kwargs)
        context['election'] = self.object.writeitinstance.election
        return context

