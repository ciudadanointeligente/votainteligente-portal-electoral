from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from popular_proposal.models import ProposalTemporaryData
from preguntales.models import Message
from django.views.generic.edit import FormView
from popular_proposal.forms import CommentsForm
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse


class IndexView(TemplateView):
    template_name='backend_staff/index.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['proposals'] = ProposalTemporaryData.objects.all()
        context['needing_moderation_messages'] = Message.objects.needing_moderation_messages()
        return context


class PopularProposalCommentsView(FormView):
    form_class = CommentsForm
    template_name = 'backend_staff/popular_proposal_comments.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(PopularProposalCommentsView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PopularProposalCommentsView, self).get_form_kwargs()
        pk = self.kwargs.pop('pk')
        temporary_data = get_object_or_404(ProposalTemporaryData, pk=pk)
        kwargs['temporary_area'] = temporary_data
        kwargs['moderator'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(PopularProposalCommentsView, self).form_valid(form)

    def get_success_url(self):
        return reverse('backend_staff:index')
