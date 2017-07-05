# coding=utf-8
from django.views.generic.edit import CreateView, DeleteView
from proposal_subscriptions.models import SearchSubscription
from django.contrib.auth.mixins import LoginRequiredMixin
from pytimeparse.timeparse import timeparse
from django.forms import ModelForm
from django.http import JsonResponse
from django import forms
import json
from django.urls import reverse_lazy
from popular_proposal.filters import ProposalGeneratedAtFilter
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _


OFTENITY_CHOICES = ((timeparse("1 day"), u"1 Día"),
                    (timeparse("2 days"), u"2 Días"),
                    (timeparse("1 weeks"), u"1 Semana"))


class SubscriptionCreateForm(ModelForm):
    oftenity = forms.ChoiceField(choices=OFTENITY_CHOICES, label=_(u"Cada cuanto quieres que te notifiquemos?"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.filter_class = kwargs.pop('filter_class')
        self.search_params = kwargs.pop('search_params')
        super(SubscriptionCreateForm, self).__init__(*args, **kwargs)

    def save(self):
        subscription = super(SubscriptionCreateForm, self).save(commit=False)
        subscription.user = self.user
        subscription.filter_class_module = self.filter_class.__module__
        subscription.filter_class_name = self.filter_class.__name__
        subscription.search_params = self.search_params
        subscription.save()
        return subscription

    class Meta:
        model = SearchSubscription
        fields = ['oftenity', ]


class SearchSubscriptionCreateView(LoginRequiredMixin, CreateView):
    form_class = SubscriptionCreateForm
    template_name = 'proposal_subscriptions/subscribe_to_search.html'
    filter_class = ProposalGeneratedAtFilter

    def get_form_kwargs(self):

        kwargs = super(SearchSubscriptionCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['filter_class'] = self.filter_class
        fields = self.filter_class().form.fields
        search_params = {}
        for field_key in fields:
            value = self.request.POST.get(field_key, None)
            if value:
                search_params[field_key] = value
        kwargs['search_params'] = search_params
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SearchSubscriptionCreateView, self).get_context_data(**kwargs)
        context['search_params_keys'] = json.dumps(self.filter_class().form.fields.keys())
        return context

    def form_valid(self, form):
        subscription = form.save()
        return JsonResponse({'subscription_id': subscription.id})


class SearchSubscriptionDeleteView(DeleteView):
    model = SearchSubscription
    slug_field = 'token'
    slug_url_kwarg = 'token'
    template_name = 'proposal_subscriptions/confirm_unsubscribe.html'
    success_url = reverse_lazy('popular_proposals:home')


class SearchSubscriptionListView(ListView):
    model = SearchSubscription
    template_name = "proposal_subscriptions/list.html"
    context_object_name = 'subscriptions'

    def get_queryset(self):
        qs = super(SearchSubscriptionListView, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs
