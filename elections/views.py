# coding=utf-8
from django.views.generic.edit import FormView
from elections.forms import ElectionSearchByTagsForm
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, TemplateView
from elections.models import Election
from elections.models import Candidate, QuestionCategory
import logging

logger = logging.getLogger(__name__)
from candidator.models import Topic, Position, TakenPosition
from candidator.comparer import Comparer, InformationHolder


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
        context['featured_elections'] = Election.objects.filter(highlighted=True)
        context['searchable_elections_enabled'] = True
        if Election.objects.filter(searchable=True).count() < 1:
            context['searchable_elections_enabled'] = False

        return context


class ElectionDetailView(DetailView):
    model = Election

    def get_context_data(self, **kwargs):
        context = super(ElectionDetailView, self).get_context_data(**kwargs)
        if 'slug_candidate_one' in self.kwargs:
            context['first_candidate'] = self.object.candidates.get(id=self.kwargs['slug_candidate_one'])
        if 'slug_candidate_two' in self.kwargs:
            context['second_candidate'] = self.object.candidates.get(id=self.kwargs['slug_candidate_two'])
        return context


class FaceToFaceView(ElectionDetailView):
    def get_context_data(self, **kwargs):
        context = super(FaceToFaceView, self).get_context_data(**kwargs)
        if 'first_candidate' in context and 'second_candidate' in context:
            candidate1, candidate2 = context['first_candidate'], context['second_candidate']
            categories = self.object.categories.all()
            equal_answers = 0
            categories = QuestionCategory.objects.filter(election=self.object)
            topics = Topic.objects.filter(category__in=categories)
            total_questions = topics.count()
            taken_positions = TakenPosition.objects.filter(topic__in=topics)
            for topic in topics:
                try:
                    taken_position1 = taken_positions.get(person=candidate1, topic=topic)
                    taken_position2 = taken_positions.get(person=candidate2, topic=topic)
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
        queryset = queryset.filter(election__slug=self.kwargs['election_slug'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        #I know this is weird but this is basically
        #me the candidate.candideitorg_election.votainteligente_election
        #so that's why it says election.election
        context['election'] = self.object.election
        return context

import re


class VotaInteligenteAdapter():
    def is_topic_category_the_same_as(self, topic, category):
        return topic.category == category.category_ptr


class SoulMateDetailView(DetailView):
    model = Election

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
                position = Position.objects.get(id=position_id)
                positions.append(TakenPosition(
                    topic=topic,
                    position=position
                    ))
        return positions

    def get_information_holder(self, data={}, adapter=VotaInteligenteAdapter):
        holder = InformationHolder(adapter=VotaInteligenteAdapter)
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
        election = super(SoulMateDetailView, self).get_object(self.get_queryset())
        self.object = election
        context = self.get_context_data()
        information_holder = self.get_information_holder(data=request.POST, adapter=VotaInteligenteAdapter)

        comparer = Comparer(adapter=VotaInteligenteAdapter)
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
