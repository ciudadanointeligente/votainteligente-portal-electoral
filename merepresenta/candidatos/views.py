from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseNotFound, HttpResponseRedirect
from backend_candidate.models import Candidacy
from backend_candidate.views import ProfileView
from .forms import CPFAndDdnForm, CPFAndDdnForm2, get_form_classes_for_questions_for
from social_core.actions import do_complete, do_auth
from social_django.views import _do_login
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from social_django.utils import psa, STORAGE, get_strategy
from django.views.generic.base import TemplateView
from backend_candidate.models import is_candidate
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from merepresenta.models import Candidate, QuestionCategory
from django.core.urlresolvers import reverse
from merepresenta.forms import PersonalDataForm
from django.shortcuts import render
from django.utils.decorators import classonlymethod
from formtools.wizard.views import SessionWizardView
from django.views.generic import DetailView

class LoginView(TemplateView):
    template_name="candidatos/login.html"

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            url = reverse_lazy('cpf_and_date2')
            return HttpResponseRedirect(url)
        return super(LoginView, self).dispatch(*args, **kwargs)


class CPFAndDDNSelectView(LoginRequiredMixin, FormView):
    form_class = CPFAndDdnForm
    template_name = 'candidatos/cpf_and_ddn.html'
    # login_url = reverse_lazy('')
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('index'))
        if self.request.user.is_staff:
            return HttpResponseNotFound()
        try:
            c = Candidacy.objects.get(user=self.request.user)
            election = c.candidate.election
            candidate = c.candidate
            url = reverse_lazy('merepresenta_complete_profile', kwargs={'slug': election.slug, 'candidate_slug': candidate.slug})
            return HttpResponseRedirect(url)
        except Candidacy.DoesNotExist:
            pass

        return super(CPFAndDDNSelectView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        original  = super(CPFAndDDNSelectView, self).get_form_kwargs()
        original['user'] = self.request.user
        return original

    def form_valid(self, form):
        form.save()
        return super(CPFAndDDNSelectView, self).form_valid(form)


    def get_success_url(self):
        c = Candidacy.objects.get(user=self.request.user)
        return c.get_complete_profile_url()


class CPFAndDDNSelectView2(FormView):
    form_class = CPFAndDdnForm2
    template_name = 'candidatos/candidato-form.html'

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_staff:
            return HttpResponseNotFound()

        if is_candidate(self.request.user):
            user = self.request.user
            candidacy = user.candidacies.first()
            url = reverse_lazy('merepresenta_complete_profile', kwargs={'slug': candidacy.candidate.election.slug,
                                                                             'candidate_slug': candidacy.candidate.slug})
            return HttpResponseRedirect(url)
        return super(CPFAndDDNSelectView2, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        self.candidate = form.get_candidate()
        context = {'candidate': self.candidate}
        response = render(self.request, 'candidatos/login_with_facebook.html', context)
        return response

def load_strategy(request=None):
    return get_strategy('merepresenta.candidatos.strategy.CandidateStrategy', STORAGE, request)

@never_cache
@csrf_exempt
@psa(load_strategy=load_strategy, redirect_uri='candidate_social_complete')
def complete(request, backend, *args, **kwargs):
    return do_complete(request.backend, _do_login, request.user,
                       redirect_value='next', request=request,
                       *args, **kwargs)

@never_cache
@psa('candidate_social_complete')
def auth(request, backend, slug):
    candidate = get_object_or_404(Candidate, slug=slug)
    request.backend.strategy.session_set('facebook_slug', slug)
    return do_auth(request.backend)


class CompleteProfileView(ProfileView):
    candidate_model = Candidate

    def dispatch(self, *args, **kwargs):
        candidate = get_object_or_404(self.candidate_model,
                                      slug=self.kwargs['candidate_slug'])
        if candidate.candidatequestioncategory_set.exists():
            return HttpResponseRedirect(candidate.get_absolute_url())
        return super(CompleteProfileView, self).dispatch(*args, **kwargs)

    def get_form_class(self):
        return PersonalDataForm

    def get_success_url(self):
        url = reverse('complete_pautas')
        return url


class CompletePautasWizardView(SessionWizardView):
    template_name = 'base_pautas.html'
    def process_step(self, form):
        data = self.get_form_step_data(form)
        form.save()
        return data

    def done(self, form_list, **kwargs):
        candidate = None
        context = {
            'form_data': [form.cleaned_data for form in form_list],
        }
        if form_list:
            candidate = Candidate.objects.get(candidate_ptr=form_list[0].candidate)
            context['candidate'] = candidate

        return render(self.request, 'candidatos/obrigado_pela_suas_respostas.html', context)


def get_pautas_view(request, *args, **kwargs):
    user = request.user
    if not user.is_authenticated or not user.candidacies.count():
        return HttpResponseRedirect(reverse('index'))
    candidate = request.user.candidacies.first().candidate
    forms = get_form_classes_for_questions_for(candidate)
    class OnDemandCompletePautas(CompletePautasWizardView):
        form_list = forms
    return OnDemandCompletePautas.as_view()(request, *args, **kwargs)


class MeRepresentaCandidateDetailView(DetailView):
    model = Candidate
    slug_field = 'slug'
    context_object_name = 'candidate'
    template_name='merepresenta/candidate_detail.html'


    def get_context_data(self, *args, **kwargs):
        context = super(MeRepresentaCandidateDetailView, self).get_context_data(*args, **kwargs)
        context['categories'] = QuestionCategory.objects.all()
        return context
