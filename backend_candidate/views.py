from backend_candidate.models import is_candidate, CandidacyContact, Candidacy
from django.http import Http404
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from backend_candidate.forms import get_form_for_election
from elections.models import Candidate, Election, PersonalData
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from backend_candidate.forms import get_candidate_profile_form_class
from popular_proposal.models import Commitment, PopularProposal
from django.contrib import messages
from django.utils.translation import ugettext as _


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


class HomeView(BackendCandidateBase, RedirectView):
    template_name = "backend_candidate/home.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
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
    def dispatch(self, *args, **kwargs):
        self.contact = get_object_or_404(CandidacyContact,
                                         identifier=self.kwargs['identifier'])
        return super(CandidacyJoinView, self).dispatch(*args, **kwargs)

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


form_class = get_candidate_profile_form_class()


class ProfileView(FormView):
    form_class = form_class
    template_name = 'backend_candidate/complete_profile.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_candidate(request.user):
            raise Http404
        self.user = request.user
        self.election = get_object_or_404(Election, slug=self.kwargs['slug'])
        self.candidate = get_object_or_404(Candidate,
                                           id=self.kwargs['candidate_id'])
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
        for field in self.form_class.base_fields:
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
        qs = super(ProposalsForMe, self).get_queryset()
        proposals_ids = []
        for commitment in self.candidate.commitments.all():
            proposals_ids.append(commitment.proposal.id)
        qs = qs.filter(area=self.election.area).exclude(id__in=proposals_ids)
        return qs

    def get_context_data(self, **kwargs):
        context = (super(ProposalsForMe, self)
                   .get_context_data(**kwargs))
        context['candidate'] = self.candidate
        context['election'] = self.election
        return context