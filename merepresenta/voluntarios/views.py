# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from merepresenta.models import Candidate, VolunteerInCandidate, VolunteerGetsCandidateEmailLog
from braces.views import StaffuserRequiredMixin
from django.views.generic.base import TemplateView
from django.views import View
from social_core.actions import do_complete, do_auth
from social_django.views import _do_login
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from social_django.utils import psa, STORAGE, get_strategy
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django_filters.views import FilterView
from merepresenta.voluntarios.filters import CandidateFilter
from django.views.generic.edit import UpdateView
from .forms import UpdateAreaForm, VoluntarioCandidateHuntForm, AddCandidacyContactForm
from .models import VolunteerProfile
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render


class VolunteerIndexView(StaffuserRequiredMixin, FilterView):
    model = Candidate
    login_url = reverse_lazy(u"volunteer_login")
    template_name = "voluntarios/index.html"
    context_object_name = 'candidates'
    filterset_class = CandidateFilter

    def dispatch(self, *args, **kwargs):
        if not settings.MEREPRESENTA_VOLUNTARIOS_ON and not self.request.user.is_staff:
            return render(self.request, 'voluntarios/voluntarios-inativo.html', {})
        return super(VolunteerIndexView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(VolunteerIndexView, self).get_context_data(*args, **kwargs)
        profile, created = VolunteerProfile.objects.get_or_create(user=self.request.user)
        context['update_area_form'] = UpdateAreaForm(instance=profile)
        return context

    def get_queryset(self):
        qs = self.model.for_volunteers.exclude(volunteerincandidate__isnull=False)
        try:
            area = self.request.user.volunteer_profile.area
            qs = qs.filter(elections__area=area)
        except VolunteerProfile.DoesNotExist:
            pass
        qs = qs.order_by('-desprivilegio')
            
        return qs

# voluntarios_login_template_name = 'voluntarios/voluntarios-inativo.html'
# if settings.MEREPRESENTA_VOLUNTARIOS_ON:
#     voluntarios_login_template_name = 'voluntarios/login.html'
class VolunteerLoginView(TemplateView):
    template_name = 'voluntarios/login.html'

    def dispatch(self, *args, **kwargs):
        if not settings.MEREPRESENTA_VOLUNTARIOS_ON:
            context = self.get_context_data()
            return render(self.request, 'voluntarios/voluntarios-inativo.html', context)
        if self.request.user.is_authenticated:
            if not self.request.user.is_staff:
                return HttpResponseNotFound()
            return HttpResponseRedirect(reverse_lazy('volunteer_index'))
        return super(VolunteerLoginView, self).dispatch(*args, **kwargs)


def load_strategy(request=None):
    return get_strategy('merepresenta.voluntarios.strategy.VolunteerStrategy', STORAGE, request)

@never_cache
@csrf_exempt
@psa(load_strategy=load_strategy, redirect_uri='volunteer_social_complete')
def complete(request, backend, *args, **kwargs):
    return do_complete(request.backend, _do_login, request.user,
                       redirect_value='next', request=request,
                       *args, **kwargs)

@never_cache
@psa('volunteer_social_complete')
def auth(request, backend):
    return do_auth(request.backend)

class AddMailToCandidateView(StaffuserRequiredMixin, FormView):
    form_class = VoluntarioCandidateHuntForm
    login_url = reverse_lazy(u"volunteer_login")
    template_name = 'voluntarios/add_email_to_candidate.html'
    
    def get_success_url(self): 
        return reverse_lazy('obrigado')

    def dispatch(self, *args, **kwargs):
        if not settings.MEREPRESENTA_VOLUNTARIOS_ON  and not self.request.user.is_staff:
            return HttpResponseRedirect('/')
        _id = kwargs['id']
        self.candidate = get_object_or_404(Candidate, id=_id)
        if self.request.user.is_authenticated() and self.request.user.is_staff:
            self.record = VolunteerInCandidate.objects.get_or_create(candidate=self.candidate,
                                                                     volunteer=self.request.user)
        return super(AddMailToCandidateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AddMailToCandidateView, self).get_form_kwargs()

        kwargs['candidate'] = self.candidate
        kwargs['volunteer'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(AddMailToCandidateView, self).form_valid(form)



class ObrigadoView(StaffuserRequiredMixin, TemplateView):
    template_name=u'voluntarios/obrigado.html'


## Mierda! esta clase no debería depender de StaffuserRequiredMixin ni de TemplateView
## Los mixins dependen sólo de object!!!! Mierda Mierda.
## lo cambio lego
class UpdateOnlyOneFieldMixin(StaffuserRequiredMixin, TemplateView):
    login_url = reverse_lazy(u"volunteer_login")
    def dispatch(self, *args, **kwargs):
        _id = kwargs['id']
        self.candidate = get_object_or_404(Candidate, id=_id)
        setattr(self.candidate, self.field, self.resulting_value)
        self.candidate.save()
        return super(UpdateOnlyOneFieldMixin, self).dispatch(*args, **kwargs)

class CouldNotFindCandidate(UpdateOnlyOneFieldMixin):
    template_name=u'voluntarios/sorry.html'
    
    field = 'is_ghost'
    resulting_value = True

    

class FacebookContacted(UpdateOnlyOneFieldMixin):
    template_name = u'voluntarios/obrigado.html'
    field = 'facebook_contacted'
    resulting_value = True


    def get(self, *args, **kwargs):
        response = super(FacebookContacted, self).get(*args, **kwargs)
        VolunteerGetsCandidateEmailLog.objects.create(candidate=self.candidate,
                                                      volunteer=self.request.user)
        return response


class UpdateAreaOfVolunteerView(StaffuserRequiredMixin, UpdateView):
    form_class = UpdateAreaForm
    model = VolunteerProfile
    login_url = reverse_lazy(u"volunteer_login")
    template_name = 'voluntarios/update_area_of_volunteer.html'

    def get_object(self):
        return self.request.user.volunteer_profile

    def get_success_url(self):
        return reverse_lazy('volunteer_index')
