from social_django.strategy import DjangoStrategy
from django.shortcuts import resolve_url


class VolunteerStrategy(DjangoStrategy):

    def get_setting(self, name):
        if name in ['NEW_USER_REDIRECT_URL', 'LOGIN_REDIRECT_URL']:
            return resolve_url('volunteer_login')
        return super(VolunteerStrategy, self).get_setting(name)

    def create_user(self, *args, **kwargs):
        user = super(VolunteerStrategy, self).create_user(*args, is_staff=True, **kwargs)
        return user