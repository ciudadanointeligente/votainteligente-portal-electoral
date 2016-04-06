from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from popular_proposal.models import ProposalTemporaryData
from preguntales.models import Message
from django.views.generic.edit import FormView
from popular_proposal.forms import CommentsForm, RejectionForm
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect


class IndexView(TemplateView):
    template_name='backend_staff/index.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['proposals'] = ProposalTemporaryData.needing_moderation.all()
        context['needing_moderation_messages'] = Message.objects.needing_moderation_messages()
        return context


class PopularProposalCommentsView(FormView):
    form_class = CommentsForm
    template_name = 'backend_staff/popular_proposal_comments.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        pk = self.kwargs.pop('pk')
        self.temporary_data = get_object_or_404(ProposalTemporaryData, pk=pk)
        return super(PopularProposalCommentsView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PopularProposalCommentsView, self).get_form_kwargs()
        kwargs['temporary_area'] = self.temporary_data
        kwargs['moderator'] = self.request.user
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(PopularProposalCommentsView, self).get_context_data(*args, **kwargs)
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
    def dispatch(self, *args, **kwargs):
        return super(ModeratePopularProposalView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(ModeratePopularProposalView, self).get_context_data(*args, **kwargs)
        pk = self.kwargs.pop('pk')
        temporary_data = get_object_or_404(ProposalTemporaryData, pk=pk)

        context['form'] = RejectionForm(temporary_area=temporary_data,
                                        moderator=self.request.user)
        return context


class AcceptPopularProposalView(View, SingleObjectMixin):
    model = ProposalTemporaryData

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(AcceptPopularProposalView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        temporary_data = self.get_object()
        temporary_data.create_proposal(moderator=self.request.user)
        return HttpResponseRedirect(reverse('backend_staff:index'))

class RejectPopularProposalView(FormView):
    form_class = RejectionForm
    template_name = 'backend_staff/index.html'
    http_method_names = ['post',]

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(RejectPopularProposalView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(RejectPopularProposalView, self).get_form_kwargs()
        pk = self.kwargs.pop('pk')
        temporary_data = get_object_or_404(ProposalTemporaryData, pk=pk)
        kwargs['temporary_area'] = temporary_data
        kwargs['moderator'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.reject()
        return super(RejectPopularProposalView, self).form_valid(form)

    def get_success_url(self):
        return reverse('backend_staff:index')
