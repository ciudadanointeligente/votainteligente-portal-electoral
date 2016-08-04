from backend_candidate.models import is_candidate, CandidacyContact, Candidacy
from django.http import Http404
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
from backend_candidate.forms import get_form_for_election
from elections.models import Candidate, Election
from django.core.urlresolvers import reverse


class BackendCandidateBase(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_candidate(request.user):
            raise Http404
        self.user = request.user
        return super(BackendCandidateBase, self).dispatch(request,
                                                          *args,
                                                          **kwargs)


class HomeView(BackendCandidateBase, TemplateView):
    template_name = "backend_candidate/home.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context['candidacies'] = self.user.candidacies.all()
        return context

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
        return super(CompleteMediaNaranjaView, self).form_valid(form)

    def get_success_url(self):
        return reverse('backend_candidate:home')


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
        return reverse('backend_candidate:home')
