from backend_candidate.models import is_candidate, CandidacyContact, Candidacy, CandidateIncremental
from django.http import Http404
from django.views.generic.base import RedirectView
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, CreateView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from backend_candidate.forms import get_form_for_election
from elections.models import Candidate, Election, PersonalData
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from backend_candidate.forms import get_candidate_profile_form_class
from popular_proposal.models import Commitment, PopularProposal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext as _
from agenda.models import Activity
from popular_proposal.filters import ProposalWithoutAreaFilter
from django.views.generic.detail import DetailView
from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import render
from constance import config


class BackendCandidateBase(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_candidate(request.user):
            raise Http404
        self.user = request.user
        candidacy_objects = CandidacyContact.objects.filter(candidacy__user=self.user)
        used_by_candidate = True
        for candidacy_object in candidacy_objects:

            if not candidacy_object.used_by_candidate:
                used_by_candidate = False
                candidacy_object.used_by_candidate = True
                candidacy_object.save()
        if not used_by_candidate:
            return HttpResponseRedirect(reverse('password_reset'))
        return super(BackendCandidateBase, self).dispatch(request,
                                                          *args,
                                                          **kwargs)


class HelpFindingCandidates(ListView):
    template_name = "backend_candidate/help_finding_candidates.html"
    model = Candidate
    context_object_name = 'candidates'

    def get_queryset(self):
        qs = super(HelpFindingCandidates, self).get_queryset().distinct()
        qs = qs.filter(contact_details__contact_type__in=['TWITTER', 'FACEBOOK'])
        return qs

class HomeView(BackendCandidateBase, RedirectView):
    template_name = "backend_candidate/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['candidacies'] = self.user.candidacies.all()
        return context

    def get_redirect_url(self, *args, **kwargs):
        candidacy = self.user.candidacies.first()
        profile_url = reverse('backend_candidate:complete_profile',
                              kwargs={'slug': candidacy.candidate.election.slug,
                                      'candidate_id': candidacy.candidate.id})
        return profile_url


class CompleteMediaNaranjaView(FormView):
    template_name = 'backend_candidate/complete_12_naranja.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_candidate(request.user):
            raise Http404
        self.user = request.user
        self.election = get_object_or_404(Election, slug=self.kwargs['slug'])
        self.candidate = get_object_or_404(Candidate,
                                           id=self.kwargs['candidate_id'])
        return super(CompleteMediaNaranjaView, self).dispatch(request,
                                                              *args,
                                                              **kwargs)

    def get_form_class(self):
        return get_form_for_election(self.election)

    def get_form_kwargs(self):
        kwargs = super(CompleteMediaNaranjaView, self).get_form_kwargs()
        kwargs['candidate'] = self.candidate
        return kwargs

    def get_context_data(self, **kwargs):
        context = (super(CompleteMediaNaranjaView, self)
                   .get_context_data(**kwargs))
        context['candidate'] = self.candidate
        context['election'] = self.election
        return context

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.INFO, _('Hemos guardado tus respuestas'))
        return super(CompleteMediaNaranjaView, self).form_valid(form)

    def get_success_url(self):
        url = reverse('backend_candidate:complete_12_naranja',
                      kwargs={'slug': self.election.slug,
                              'candidate_id': self.candidate.id})
        return url


class CandidacyJoinView(RedirectView):
    permanent = False
    query_string = True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(CandidacyContact,
                                         identifier=self.kwargs['identifier'])
        return super(CandidacyJoinView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        candidacy, created = Candidacy.objects.get_or_create(candidate=self.contact.candidate,
                                                             user=self.request.user
                                                             )
        self.contact.candidacy = candidacy
        self.contact.used_by_candidate = True
        self.contact.save()
        candidacy = self.request.user.candidacies.first()
        profile_url = reverse('backend_candidate:complete_profile',
                              kwargs={'slug': candidacy.candidate.election.slug,
                                      'candidate_id': candidacy.candidate.id})
        return profile_url


class ProfileView(FormView):
    template_name = 'backend_candidate/complete_profile.html'

    def get_form_class(self):
        return get_candidate_profile_form_class()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_candidate(request.user):
            raise Http404
        self.user = request.user
        self.election = get_object_or_404(Election, slug=self.kwargs['slug'])
        self.candidate = get_object_or_404(Candidate,
                                           id=self.kwargs['candidate_id'])
        if not Candidacy.objects.filter(user=self.request.user, candidate=self.candidate).exists():
            raise Http404
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ProfileView, self).get_form_kwargs()
        kwargs['candidate'] = self.candidate
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.INFO, _('Hemos actualizado tu perfil'))
        return super(ProfileView, self).form_valid(form)

    def get_success_url(self):
        url = reverse('backend_candidate:complete_profile',
                      kwargs={'slug': self.election.slug,
                              'candidate_id': self.candidate.id}
                      )
        return url

    def get_initial(self):
        initial = super(ProfileView, self).get_initial()
        labels = []
        for field in self.get_form_class().base_fields:
            labels.append(field)
        personal_datas = PersonalData.objects.filter(candidate=self.candidate,
                                                     label__in=labels)
        for personal_data in personal_datas:
            initial[str(personal_data.label)] = personal_data.value
        return initial

    def get_context_data(self, **kwargs):
        context = (super(ProfileView, self)
                   .get_context_data(**kwargs))
        context['candidate'] = self.candidate
        context['election'] = self.election
        return context


class MyCommitments(BackendCandidateBase, ListView):
    model = Commitment
    template_name = 'backend_candidate/i_have_commited.html'
    context_object_name = 'commitments'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_candidate(request.user):
            raise Http404
        self.user = request.user
        self.election = get_object_or_404(Election, slug=self.kwargs['slug'])
        self.candidate = get_object_or_404(Candidate,
                                           id=self.kwargs['candidate_id'])
        return super(MyCommitments, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(MyCommitments, self).get_queryset()
        return qs.filter(candidate=self.candidate)

    def get_context_data(self, **kwargs):
        context = (super(MyCommitments, self)
                   .get_context_data(**kwargs))
        context['candidate'] = self.candidate
        context['election'] = self.election
        return context


class ProposalsForMe(BackendCandidateBase, ListView):
    model = PopularProposal

    template_name = 'backend_candidate/proposals_for_me.html'
    context_object_name = 'proposals'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_candidate(request.user):
            raise Http404
        self.user = request.user
        self.election = get_object_or_404(Election, slug=self.kwargs['slug'])
        self.candidate = get_object_or_404(Candidate,
                                           id=self.kwargs['candidate_id'])
        return super(ProposalsForMe, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = ProposalWithoutAreaFilter().qs.by_likers()
        proposals_ids = []
        for commitment in self.candidate.commitments.all():
            proposals_ids.append(commitment.proposal.id)
        if not self.election.candidates_can_commit_everywhere:
            qs = qs.filter(area=self.election.area)
        qs = qs.exclude(id__in=proposals_ids)
        return qs

    def get_context_data(self, **kwargs):
        context = (super(ProposalsForMe, self)
                   .get_context_data(**kwargs))
        context['candidate'] = self.candidate
        context['election'] = self.election
        return context


from agenda.forms import ActivityForm


class AddActivityToCandidateView(LoginRequiredMixin, CreateView):
    form_class = ActivityForm
    template_name = 'backend_candidate/add_activity.html'

    def get_content_object(self):
        self.candidate = get_object_or_404(Candidate,
                                           id=self.kwargs['slug'])
        get_object_or_404(Candidacy,
                          candidate=self.candidate,
                          user=self.request.user)
        return self.candidate

    def get_form_kwargs(self):
        kwargs = super(AddActivityToCandidateView, self).get_form_kwargs()
        kwargs['content_object'] = self.get_content_object()
        return kwargs

    def get_success_url(self):
        return reverse('backend_candidate:all_my_activities',
                        kwargs={'slug': self.candidate.id})

    def get_context_data(self, **kwargs):
        context = super(AddActivityToCandidateView, self).get_context_data(**kwargs)
        context['object'] = self.candidate
        return context


class MyActivitiesListView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = 'backend_candidate/all_my_activities.html'
    context_object_name = 'activities'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Candidate,
                                           id=self.kwargs['slug'])
        get_object_or_404(Candidacy,
                          candidate=self.object,
                          user=self.request.user)
        return super(MyActivitiesListView, self).dispatch(request,
                                                          *args,
                                                          **kwargs)

    def get_queryset(self):
        return self.object.agenda.all()

    def get_context_data(self, **kwargs):
        context = super(MyActivitiesListView, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context


class CandidateIncrementalDetailView(DetailView):
    model = CandidateIncremental
    slug_url_kwarg = "identifier"
    slug_field = 'identifier'
    

    def get_queryset(self):
        qs = super(CandidateIncrementalDetailView, self).get_queryset()
        return qs


    def get_context_data(self, **kwargs):
        context = super(CandidateIncrementalDetailView, self).get_context_data(**kwargs)
        context['formset'] = self.object.formset
        context['candidate_incremental'] = self.object
        context['site'] = Site.objects.get_current()
        context['text'] = self.object.suggestion.text
        context['candidate'] = self.object.candidate
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.used = True
        self.object.save()
        CommitmentIcrementalFormset = self.object._formset_class
        formset = CommitmentIcrementalFormset(request.POST, request.FILES)
        if formset.is_valid():
            commitments = formset.save()
            if commitments:
                return render(request, 'backend_candidate/thanks_for_commiting.html', context={'commitments': commitments})
        return self.get(request, *args, **kwargs)

    def get_template_names(self):
        if settings.DEBUG and config.SHOW_MAIL_NOT_TEMPLATE:
            return ['mails/suggestions_for_candidates/body.html']
        return ['backend_candidate/suggestions_for_candidate.html']


