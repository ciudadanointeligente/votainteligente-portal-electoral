# coding=utf-8
from django.views.generic.base import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from popular_proposal.models import ProposalTemporaryData, Commitment
from django.views.generic.edit import FormView
from popular_proposal.forms import CommentsForm, RejectionForm
from backend_staff.forms import AddContactAndSendMailForm
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect, HttpResponseNotFound
from elections.models import Candidate
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from backend_staff.stats import Stats, PerAreaStaffStats
from elections.models import Area


class IndexView(TemplateView):
    template_name = 'backend_staff/index.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(IndexView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['proposals'] = ProposalTemporaryData.objects.all().order_by('-created')
        return context


class PopularProposalCommentsView(FormView):
    form_class = CommentsForm
    template_name = 'backend_staff/popular_proposal_comments.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.pop('pk')
        self.temporary_data = get_object_or_404(ProposalTemporaryData, pk=pk)
        return super(PopularProposalCommentsView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PopularProposalCommentsView, self).get_form_kwargs()
        kwargs['temporary_data'] = self.temporary_data
        kwargs['moderator'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PopularProposalCommentsView, self).get_context_data(**kwargs)
        context['temporary_data'] = self.temporary_data
        return context

    def form_valid(self, form):
        form.save()
        return super(PopularProposalCommentsView, self).form_valid(form)

    def get_success_url(self):
        return reverse('backend_staff:index')

class ModeratePopularProposalView(DetailView):
    model = ProposalTemporaryData
    template_name = 'backend_staff/proposal_moderation.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ModeratePopularProposalView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ModeratePopularProposalView, self).get_context_data(**kwargs)
        pk = self.kwargs.pop('pk')
        temporary_data = get_object_or_404(ProposalTemporaryData, pk=pk)

        context['form'] = RejectionForm(temporary_data=temporary_data,
                                        moderator=self.request.user)
        return context


class AcceptPopularProposalView(View, SingleObjectMixin):
    model = ProposalTemporaryData

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AcceptPopularProposalView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        temporary_data = self.get_object()
        temporary_data.create_proposal(moderator=self.request.user)
        return HttpResponseRedirect(reverse('backend_staff:index'))

class RejectPopularProposalView(FormView):
    form_class = RejectionForm
    template_name = 'backend_staff/index.html'
    http_method_names = ['post',]

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RejectPopularProposalView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(RejectPopularProposalView, self).get_form_kwargs()
        pk = self.kwargs.pop('pk')
        temporary_data = get_object_or_404(ProposalTemporaryData, pk=pk)
        kwargs['temporary_data'] = temporary_data
        kwargs['moderator'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.reject()
        return super(RejectPopularProposalView, self).form_valid(form)

    def get_success_url(self):
        return reverse('backend_staff:index')


class AddContactAndSendMailView(FormView):
    form_class = AddContactAndSendMailForm
    template_name = 'backend_staff/add_contact_and_send_mail.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.pop('pk')
        self.candidate = get_object_or_404(Candidate, pk=pk)
        return super(AddContactAndSendMailView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AddContactAndSendMailView, self).get_form_kwargs()
        kwargs['candidate'] = self.candidate
        return kwargs

    def form_valid(self, form):
        form.send_mail()
        return super(AddContactAndSendMailView, self).form_valid(form)

    def get_success_url(self):
        return self.candidate.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(AddContactAndSendMailView, self).get_context_data(**kwargs)
        context['candidate'] = self.candidate
        return context


class AllCommitmentsView(ListView):
    model = Commitment
    template_name = 'backend_staff/all_commitments.html'
    context_object_name = 'commitments'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.profile.is_journalist:
            return HttpResponseNotFound()
        return super(AllCommitmentsView, self).dispatch(request, *args, **kwargs)


class StatsView(TemplateView):
    template_name = 'backend_staff/stats.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StatsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatsView, self).get_context_data(**kwargs)
        context['stats'] = Stats()
        return context

class StatsPerAreaView(TemplateView):
    template_name = 'backend_staff/per_area_stats.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StatsPerAreaView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatsPerAreaView, self).get_context_data(**kwargs)
        stats = {}
        for area in Area.objects.all():
            stats[area.id] = PerAreaStaffStats(area)
        context['stats'] = stats
        return context


class ListOfUsers(ListView):
    model = User
    template_name = 'backend_staff/list_of_users.html'
    context_object_name = 'users'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ListOfUsers, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(ListOfUsers, self).get_queryset()
        qs = qs.filter(candidacies__isnull=True)
        return qs
