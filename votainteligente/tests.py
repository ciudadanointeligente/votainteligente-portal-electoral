# coding=utf-8
from django.test import TestCase
from django.contrib.auth.models import User


PASSWORD = 'SECR3T'


class VotaInteligenteAuthenticationBackend(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="the_user", password=PASSWORD, email='perrito@gmail.com')

    def test_login_using_username(self):
        login_result = self.client.login(username=self.user.username, password=PASSWORD)
        self.assertTrue(login_result)

    def test_login_using_email(self):
        login_result = self.client.login(username=self.user.email, password=PASSWORD)
        self.assertTrue(login_result)
