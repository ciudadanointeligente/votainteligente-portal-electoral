# coding=utf-8
from django.views.generic import DetailView, CreateView
from elections.models import Election, Candidate
from preguntales.forms import MessageForm
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.mail import mail_admins
from elections.views import CandidateDetailView
from django.db.models import Q
from preguntales.models import Message, Answer
from operator import itemgetter
from django.shortcuts import get_object_or_404


class MessageDetailView(DetailView):
    model = Message
    context_object_name = 'votainteligentemessage'

    def get_context_data(self, **kwargs):
        context = super(MessageDetailView, self).get_context_data(**kwargs)
        election = Election.objects.get(slug=self.kwargs['election_slug'])
        context['election'] = election
        return context


class ElectionAskCreateView(CreateView):
    model = Message
    form_class = MessageForm

    def dispatch(self, *args, **kwargs):
        if 'slug' in kwargs:
            self.election = Election.objects.get(slug = kwargs['slug'])
        return super(ElectionAskCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ElectionAskCreateView, self).get_context_data(**kwargs)
        context['election'] = self.election
        context['writeitmessages'] = Message.objects.filter(election=self.election)
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


class QuestionsPerCandidateView(CandidateDetailView):
    def get_queryset(self):
        queryset = super(QuestionsPerCandidateView, self).get_queryset()
        election_slug = self.kwargs['election_slug']
        queryset.filter(Q(elections__slug=election_slug))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(QuestionsPerCandidateView, self)\
            .get_context_data(**kwargs)
        messages = Message.objects.filter(people=self.object)
        context['questions'] = messages
        return context


class RankingMixin(object):
        candidate_queryset = None
        votainteligentemessages = None

        def __init__(self, *args, **kwargs):
            super(RankingMixin, self).__init__(*args, **kwargs)

        def get_ranking(self):
            return self.candidate_queryset

        def all_messages(self):
            if not self.votainteligentemessages:
                self.votainteligentemessages = Message.objects\
                    .filter(people__in=self.candidate_queryset).distinct()
            return self.votainteligentemessages

        def all_possible_answers(self):
            answers = self.all_messages()
            total_possible_answers = 0
            for answer in answers:
                total_possible_answers += answer.people.count()
            return total_possible_answers

        def actual_answers(self):
            messages = self.all_messages()
            actual_count = 0
            for message in messages:
                actual_count += message.answers_.count()
            return actual_count

        def success_index(self):
            all_possible_answers = float(self.all_possible_answers())
            actual_answers = float(self.actual_answers())
            return all_possible_answers/actual_answers

        def get_clasified(self):
            clasified = []
            messages = self.all_messages()
            if not messages:
                return []
            are_there_answers = Answer.objects.\
                filter(message__in=messages).exists()
            if not are_there_answers:
                return []
            success_index = self.success_index()
            for candidate in self.candidate_queryset:
                possible_answers = Message.objects.\
                    filter(Q(people=candidate)).count()
                actual_answers = Answer.objects.\
                    filter(Q(person=candidate) & Q(message__in=messages)).\
                    count()
                points = (success_index + 1)*possible_answers*actual_answers\
                    - possible_answers*possible_answers
                clasified.append({'id': candidate.id,
                                  'name': candidate.name,
                                  'candidate': candidate,
                                  'possible_answers': possible_answers,
                                  'actual_answers': actual_answers,
                                  'points': points
                                  })
            return clasified

        def get_ordered(self):
            clasified = self.get_clasified()
            clasified = sorted(clasified,  key=itemgetter('points'),
                               reverse=True)

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
        queryset = the_object.candidates.all()
        self.candidate_queryset = queryset
        return the_object

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['good'] = self.get_good()
        context['bad'] = self.get_bad()
        return context


class ConfirmationView(DetailView):
    model = Message
    template_name = 'preguntales/confirmation.html'

    def get_queryset(self):
        return self.model.objects.filter(confirmation__isnull=False).filter(confirmation__when_confirmed__isnull=True)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        self.key = self.kwargs['key']
        message = get_object_or_404(queryset, confirmation__key=self.key)
        message.confirm()
        return message

