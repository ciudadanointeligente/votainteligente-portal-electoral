# coding=utf-8
from django.views.generic.edit import FormView
from elections.forms import ElectionSearchByTagsForm
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, TemplateView
from elections.models import Election, VotaInteligenteMessage,\
    VotaInteligenteAnswer
from elections.models import Candidate, QuestionCategory, CandidateFlatPage
import logging
from django.db.models import Q
from operator import itemgetter
logger = logging.getLogger(__name__)
from candidator.models import Topic, Position, TakenPosition
from candidator.comparer import Comparer, InformationHolder
from candidator.adapters import CandidatorCalculator, CandidatorAdapter
from popolo.models import Area


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
        context = super(ElectionsSearchByTagView, self)\
            .get_context_data(**kwargs)
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse('tags_search')


class HomeView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['form'] = ElectionSearchByTagsForm()
        context['featured_elections'] = Election.objects\
            .filter(highlighted=True)
        context['searchable_elections_enabled'] = True
        if Election.objects.filter(searchable=True).count() < 1:
            context['searchable_elections_enabled'] = False

        return context


class ElectionDetailView(DetailView):
    model = Election

    def get_context_data(self, **kwargs):
        context = super(ElectionDetailView, self).get_context_data(**kwargs)
        if 'slug_candidate_one' in self.kwargs:
            context['first_candidate'] = self.object.candidates\
                .get(id=self.kwargs['slug_candidate_one'])
        if 'slug_candidate_two' in self.kwargs:
            context['second_candidate'] = self.object.candidates\
                .get(id=self.kwargs['slug_candidate_two'])
        return context


class FaceToFaceView(ElectionDetailView):
    def get_context_data(self, **kwargs):
        context = super(FaceToFaceView, self).get_context_data(**kwargs)
        if 'first_candidate' in context and 'second_candidate' in context:
            candidate1, candidate2 = context['first_candidate'], \
                context['second_candidate']
            categories = self.object.categories.all()
            equal_answers = 0
            categories = QuestionCategory.objects.filter(election=self.object)
            topics = Topic.objects.filter(category__in=categories)
            total_questions = topics.count()
            taken_positions = TakenPosition.objects.filter(topic__in=topics)
            for topic in topics:
                try:
                    taken_position1 = taken_positions\
                        .get(person=candidate1, topic=topic)
                    taken_position2 = taken_positions\
                        .get(person=candidate2, topic=topic)
                    if taken_position2.position == taken_position1.position:
                        equal_answers += 1
                except TakenPosition.DoesNotExist:
                    pass
            if total_questions:
                context['similitude'] = equal_answers * 100 / total_questions
            else:
                context['similitude'] = 0
        return context


class CandidateDetailView(DetailView):
    model = Candidate
    slug_field = 'id'

    def get_queryset(self):
        queryset = super(CandidateDetailView, self).get_queryset()
        queryset = queryset.filter(elections__slug=self.kwargs['election_slug'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        context['election'] = self.object.election
        return context

import re


class VotaInteligenteAdapter(CandidatorAdapter):
    def is_topic_category_the_same_as(self, topic, category):
        return topic.category == category.category_ptr


class SoulMateDetailView(DetailView):
    model = Election
    adapter_class = VotaInteligenteAdapter
    calculator_class = CandidatorCalculator

    def determine_taken_positions(self, positions_dict):
        positions = []
        for key in positions_dict:
            p = re.compile('^question-id-(?P<id>\d+)$')
            m = p.search(key)
            if m:
                _id = int(m.group('id'))
                position_id = positions_dict["question-%d" % (_id)]
                topic_id = positions_dict[key]
                topic = Topic.objects.get(id=topic_id)
                try:
                    position = Position.objects.get(id=position_id)
                    positions.append(TakenPosition(
                        topic=topic,
                        position=position
                        ))
                except Position.DoesNotExist:
                    pass
        return positions

    def get_information_holder(self, data={}):
        holder = InformationHolder(adapter=self.adapter_class)
        for category in self.object.categories.all():
            holder.add_category(category)
        for candidate in self.object.candidates.all():
            holder.add_person(candidate)
        if data:
            taken_positions = self.determine_taken_positions(data)
            for taken_position in taken_positions:
                holder.add_position(taken_position)
        return holder

    def post(self, request, *args, **kwargs):
        self.template_name = "elections/soulmate_response.html"
        election = super(SoulMateDetailView, self)\
            .get_object(self.get_queryset())
        self.object = election
        context = self.get_context_data()
        information_holder = self.get_information_holder(data=request.POST)

        comparer = Comparer(adapter_class=self.adapter_class,
                            calculator_class=self.calculator_class)
        result = comparer.compare(information_holder)

        winner_candidate = result[0]['person']
        context['winner'] = result[0]
        context['winner']['candidate'] = winner_candidate

        others_candidates = []
        for other in result[1:]:
            other_candidate = other['person']
            other["candidate"] = other_candidate
            others_candidates.append(other)

        context['others'] = others_candidates
        return self.render_to_response(context)


class AreaDetailView(DetailView):
    model = Area
    context_object_name = 'area'
    template_name = 'area.html'
    slug_field = 'id'


class CandidateFlatPageDetailView(DetailView):
    model = CandidateFlatPage
    context_object_name = 'flatpage'
    template_name = 'flatpages/candidate_flatpages.html'

    def get_queryset(self):
        qs = CandidateFlatPage.objects.filter(candidate__id=self.kwargs['slug'])
        return qs

    def get_object(self, queryset=None):
        print self.kwargs['url']
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.get(url=self.kwargs['url'])

    def get_context_data(self, **kwargs):
        context = super(CandidateFlatPageDetailView, self)\
            .get_context_data(**kwargs)
        context['election'] = self.object.candidate.election
        context['candidate'] = self.object.candidate
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
                self.votainteligentemessages = VotaInteligenteMessage.objects\
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
                actual_count += message.answers.count()
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
            are_there_answers = VotaInteligenteAnswer.objects.\
                filter(message__in=messages).exists()
            if not are_there_answers:
                return []
            success_index = self.success_index()
            for candidate in self.candidate_queryset:
                possible_answers = VotaInteligenteMessage.objects.\
                    filter(Q(people=candidate)).count()
                actual_answers = VotaInteligenteAnswer.objects.\
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
