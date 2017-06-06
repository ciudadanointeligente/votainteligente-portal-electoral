from django.views.generic import TemplateView
from django.dispatch import receiver
from registration.signals import user_activated
from django.contrib.auth import login


@receiver(user_activated)
def post_activated_user(sender, user, request, **kwargs):
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)


class HomeViewBase(TemplateView):
    template_name = 'index.html'
