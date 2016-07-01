from django.shortcuts import render
from backend_candidate.models import is_candidate
from django.http import Http404
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class HomeView(TemplateView):
    template_name = "backend_candidate/home.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_candidate(request.user):
            raise Http404
        self.user = request.user
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context['candidacies'] = self.user.candidacies.all()
        return context
