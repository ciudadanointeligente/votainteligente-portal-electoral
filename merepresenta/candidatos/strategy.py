from social_django.strategy import DjangoStrategy
from django.shortcuts import resolve_url
from django.contrib.auth import authenticate


class CandidateStrategy(DjangoStrategy):

    def get_setting(self, name):
        if name in ['NEW_USER_REDIRECT_URL', 'LOGIN_REDIRECT_URL', 'SOCIAL_AUTH_FACEBOOK_LOGIN_REDIRECT_URL']:
            return resolve_url('cpf_and_date')
        return super(CandidateStrategy, self).get_setting(name)

    def create_user(self, *args, **kwargs):
        user = super(CandidateStrategy, self).create_user(*args, **kwargs)
        return user

    def authenticate(self, backend, *args, **kwargs):
        kwargs['strategy'] = self
        kwargs['storage'] = self.storage
        kwargs['backend'] = backend
        if 'request' in kwargs:
            kwargs.pop('request')
        return authenticate(*args, **kwargs)