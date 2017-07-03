# coding=utf-8
from django.shortcuts import render
from django.views.generic.edit import CreateView
from proposal_subscriptions.models import SearchSubscription
from django.contrib.auth.mixins import LoginRequiredMixin
from pytimeparse.timeparse import timeparse
from django.forms import ModelForm
from django.http import JsonResponse
import json
from popular_proposal.filters import ProposalGeneratedAtFilter


OFTENITY_CHOICES = ((timeparse("1 day"), u"1 Día"),(timeparse("2 days"), u"1 Días"), (timeparse("1 weeks"), u"1 Semana"))

class SubscriptionCreateForm(ModelForm):
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
                search_params[field_key]  = value
        kwargs['search_params'] = search_params
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SearchSubscriptionCreateView, self).get_context_data(**kwargs)
        context['search_params_keys'] = json.dumps(self.filter_class().form.fields.keys())
        return context

    def form_valid(self, form):
        subscription = form.save()
        return JsonResponse({'subscription_id': subscription.id})
