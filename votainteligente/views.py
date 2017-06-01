from django.views.generic import TemplateView
from django.dispatch import receiver
from registration.signals import user_activated
from django.contrib.auth import login
from django.shortcuts import redirect


@receiver(user_activated)
def post_activated_user(sender, user, request, **kwargs):
    login(request, user, backend='registration.backends.hmac')
    redirect('/')


class HomeViewBase(TemplateView):
    template_name = 'index.html'
