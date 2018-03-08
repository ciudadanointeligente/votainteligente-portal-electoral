# coding=utf-8
from django.views.generic.edit import FormView
from elections.forms import ElectionSearchByTagsForm
from django.core.urlresolvers import reverse
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from elections.models import Election, Area
from elections.models import Candidate, QuestionCategory, CandidateFlatPage
from votainteligente.views import HomeViewBase
import logging
from backend_citizen.forms import GroupCreationForm
from candidator.models import Topic, TakenPosition
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from backend_citizen.forms import UserCreationForm as RegistrationForm
from popular_proposal.models import PopularProposal
from popular_proposal.filters import ProposalFilterBase
from django_filters.views import FilterMixin
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from constance import config

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


class HomeView(HomeViewBase):
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['form'] = ElectionSearchByTagsForm()

        featured_elections = cache.get('featured_elections')
        if featured_elections is None:
            featured_elections = Election.objects.filter(highlighted=True)
            cache.set('featured_elections', featured_elections, 600)
        context['featured_elections'] = featured_elections

        context['searchable_elections_enabled'] = True
        context['register_new_form'] = RegistrationForm()
        context['login_form'] = AuthenticationForm()
        context['group_login_form'] = GroupCreationForm()
        total_proposals = cache.get('total_proposals')
        if total_proposals is None:
            total_proposals = PopularProposal.objects.count()
            cache.set('total_proposals', total_proposals, 600)
        context['total_proposals'] = total_proposals
        proposals_with_likers = cache.get('proposals_with_likers')
        if proposals_with_likers is None:
            proposals_with_likers = PopularProposal.ordered.by_likers()[:9]
            cache.set('proposals_with_likers', proposals_with_likers, 600)
        context['proposals_with_likers'] = proposals_with_likers
        featured_proposals = cache.get('featured_proposals')
        if featured_proposals is None:
            featured_proposals = PopularProposal.objects.filter(featured=True).filter(content_type__app_label="popular_proposal")
            cache.set('featured_proposals', featured_proposals, 600)
        context['featured_proposals'] = featured_proposals
        featured_candidates = cache.get('featured_candidates')
        if featured_candidates is None:
            featured_candidates = Candidate.objects.filter(commitments__isnull=False).filter(elections__name="Presidencia")
            cache.set('featured_candidates', featured_candidates)
        context['candidates'] = featured_candidates
        return context


class ElectionDetailViewBase(DetailView):
    model = Election


class ElectionDetailView(ElectionDetailViewBase):

    def get_context_data(self, **kwargs):
        context = super(ElectionDetailView, self).get_context_data(**kwargs)
        if 'slug_candidate_one' in self.kwargs:
            if self.object.candidates.filter(id=self.kwargs['slug_candidate_one']).exists():
                context['first_candidate'] = self.object.candidates\
                    .get(id=self.kwargs['slug_candidate_one'])
        if 'slug_candidate_two' in self.kwargs:
            if self.object.candidates.filter(id=self.kwargs['slug_candidate_two']).exists():
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
        candidates_per_election_key = u'candidates_for_' + self.get_cache_post_fix()
        queryset_ = cache.get(candidates_per_election_key)
        if queryset_ is None:

            if 'election_slug' in self.kwargs.keys():
                queryset_ = queryset.filter(elections__slug=self.kwargs['election_slug'])
            if 'area_slug' in self.kwargs.keys():
                queryset_ = queryset.filter(elections__area__slug=self.kwargs['area_slug'])
            cache.set(candidates_per_election_key,
                      queryset_,
                      60 * config.INFINITE_CACHE
                      )

        return queryset_
    def get_cache_post_fix(self):
        cache_key = ""
        kwarg_keys = self.kwargs.keys()
        kwarg_keys.remove('slug')
        for k in kwarg_keys:
            cache_key += self.kwargs.get(k)
        cache_key += self.kwargs['slug']
        return cache_key

    def get_object(self, queryset=None):
        cache_key = 'candidate_' + self.get_cache_post_fix()
        candidate = cache.get(cache_key)
        if candidate is None:
            candidate = super(CandidateDetailView, self).get_object(queryset)
            cache.set(cache_key, candidate, 60 * config.INFINITE_CACHE)
        cache_key = u'ranking-for-' + candidate.id
        _candidate = cache.get(cache_key)
        if _candidate is None:
            try:
                _candidate = self.model.ranking.filter(id=candidate.id).last()
            except self.model.DoesNotExist:
                raise Http404(u"Este candidato no existe")
            cache.set(cache_key,
                      _candidate,
                      60 * config.SOUL_MATE_INFO_ABOUT_CANDIDATES_MINUTES)
        return _candidate

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        if self.object is None:
            raise Http404(u"Este candidato no existe")
        context['election'] = self.object.election
        return context

class AreaDetailView(DetailView, FilterMixin):
    model = Area
    context_object_name = 'area'
    template_name = 'area.html'
    # slug_field = 'id'

    def dispatch(self, request, *args, **kwargs):
        area = self.get_object()
        if area.classification in settings.FILTERABLE_AREAS_TYPE and area.parent:
            return HttpResponseRedirect(Area.objects.get(id=area.parent.id).get_absolute_url())
        return super(AreaDetailView, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(AreaDetailView, self).get_context_data(**kwargs)
        initial = self.request.GET or None

        kwargs = {'data': initial or None,
                  'area': self.object
                  }
        filterset = ProposalFilterBase(**kwargs)
        context['proposal_filter_form'] = filterset.form

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


class KnowYourCandidatesView(TemplateView):
    template_name = "know_your_candidates.html"

    def get_context_data(self, **kwargs):
        context = super(KnowYourCandidatesView, self).get_context_data(**kwargs)
        election = Election.objects.filter(area__id=config.DEFAULT_AREA).first()
        if election and election.second_round:
            election = election.second_round
        context['default_election'] = election
        return context
