from social_django.strategy import DjangoStrategy
from django.shortcuts import resolve_url
from django.contrib.auth import authenticate
from .models import VolunteerProfile


class VolunteerStrategy(DjangoStrategy):

    def get_setting(self, name):
        if name in ['NEW_USER_REDIRECT_URL', 'LOGIN_REDIRECT_URL']:
            return resolve_url('volunteer_index')
        return super(VolunteerStrategy, self).get_setting(name)

    def create_user(self, *args, **kwargs):
        user = super(VolunteerStrategy, self).create_user(*args, is_staff=True, **kwargs)
        VolunteerProfile.objects.create(user=user)
        return user

    def authenticate(self, backend, *args, **kwargs):
        kwargs['strategy'] = self
        kwargs['storage'] = self.storage
        kwargs['backend'] = backend
        if 'request' in kwargs:
            kwargs.pop('request')
        return authenticate(*args, **kwargs)