from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from popular_proposal.models import ProposalTemporaryData
from preguntales.models import Message


class IndexView(TemplateView):
    template_name='backend_staff/index.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['proposals'] = ProposalTemporaryData.objects.all()
        context['needing_moderation_messages'] = Message.objects.all()
        return context
