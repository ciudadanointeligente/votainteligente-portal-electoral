from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class IndexView(LoginRequiredMixin, TemplateView):
    template_name='backend_citizen/index.html'
