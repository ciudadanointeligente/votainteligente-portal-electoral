# coding=utf-8
from django.views.generic.edit import FormView
from elections.forms import ElectionSearchByTagsForm
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, TemplateView
from elections.models import Election, Area
from elections.models import Candidate, QuestionCategory, CandidateFlatPage
import logging
from backend_citizen.forms import GroupCreationForm
from candidator.models import Topic, Position, TakenPosition
from candidator.comparer import Comparer, InformationHolder
from candidator.adapters import CandidatorCalculator, CandidatorAdapter
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from backend_citizen.forms import UserCreationForm as RegistrationForm
from popular_proposal.models import PopularProposal, ProposalTemporaryData
from popular_proposal.forms import ProposalAreaFilterForm
from popular_proposal.filters import ProposalAreaFilter
from django_filters.views import FilterMixin
import datetime
from django.utils import timezone
import re
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
        context['register_new_form'] = RegistrationForm()
        context['login_form'] = AuthenticationForm()
        context['group_login_form'] = GroupCreationForm()
        if Election.objects.filter(searchable=True).count() < 1:
            context['searchable_elections_enabled'] = False
        a_week_ago = timezone.now() - datetime.timedelta(days=7)
        context['created_proposals'] = ProposalTemporaryData.objects.filter(created__gt=a_week_ago).count()
        context['accepted_proposals'] = PopularProposal.objects.filter(created__gt=a_week_ago).count()
        context['total_proposals'] = PopularProposal.objects.count()
        context['proposals_with_likers'] = PopularProposal.ordered.by_likers()[:9]
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

    def get_object(self, queryset=None):
        candidate = super(CandidateDetailView, self).get_object(queryset)
        candidate = self.model.ranking.get(id=candidate.id)
        return candidate

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        context['election'] = self.object.election
        return context


class VotaInteligenteAdapter(CandidatorAdapter):
    def is_topic_category_the_same_as(self, topic, category):
        return topic.category == category.category_ptr


class SoulMateDetailView(DetailView):
    model = Election
    adapter_class = VotaInteligenteAdapter
    calculator_class = CandidatorCalculator
    layout = "elections/election_base.html"

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
                    positions.append(TakenPosition(topic=topic,
                                                   position=position
                                                   )
                                     )
                except Position.DoesNotExist:
                    pass
        return positions

    def get_context_data(self, **kwargs):
        context = super(SoulMateDetailView, self).get_context_data(**kwargs)
        context['layout'] = self.layout
        context['result_url'] = self.request.build_absolute_uri()
        return context

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


class AreaDetailView(DetailView, FilterMixin):
    model = Area
    context_object_name = 'area'
    template_name = 'area.html'
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        context = super(AreaDetailView, self).get_context_data(**kwargs)
        initial = self.request.GET or None
        context['proposal_filter_form'] = ProposalAreaFilterForm(area=self.object,
                                                                 initial=initial)
        kwargs = {'data': self.request.GET or None,
                  'area': self.object
                  }

        filterset = ProposalAreaFilter(**kwargs)
        context['popular_proposals'] = filterset.qs
        return context

    def get_queryset(self, *args, **kwargs):
        return Area.objects.all()


class CandidateFlatPageDetailView(DetailView):
    model = CandidateFlatPage
    context_object_name = 'flatpage'
    template_name = 'flatpages/candidate_flatpages.html'

    def get_queryset(self):
        qs = CandidateFlatPage.objects.filter(candidate__id=self.kwargs['slug'])
        return qs

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return get_object_or_404(self.model, url=self.kwargs['url'])

    def get_context_data(self, **kwargs):
        context = super(CandidateFlatPageDetailView, self)\
            .get_context_data(**kwargs)
        context['election'] = self.object.candidate.election
        context['candidate'] = self.object.candidate
        return context
