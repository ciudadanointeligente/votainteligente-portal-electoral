# coding=utf-8
from django.test import TestCase
from django.contrib.auth.models import User
import vcr
import urllib2
from backend_citizen.tasks import save_image_to_user
from backend_citizen.image_getter_from_social import get_image_from_social


PASSWORD = "perrito-chiquitito"
IMAGE_URL = 'http://graph.facebook.com/123/picture?type=large'


class VotaInteligenteGetImageFromSocial(TestCase):

    @vcr.use_cassette('backend_citizen/fixtures/vcr_cassettes/synopsis.yaml')  
    def test_image(self):
        user = User.objects.create_user(username="the_user", password=PASSWORD, email='perrito@gmail.com')
        save_image_to_user.delay(IMAGE_URL, user)
        user.refresh_from_db()
        self.assertTrue(user.profile.image)

    @vcr.use_cassette('backend_citizen/fixtures/vcr_cassettes/synopsis.yaml')
    def test_facebook_backend(self):
        class BackendFacebook(object):
            name = 'facebook'
        backend = BackendFacebook()
        user = User.objects.create_user(username="the_user", password=PASSWORD, email='perrito@gmail.com')
        response = {
            'id': 123
        }

        get_image_from_social(backend, None, None, response, user=user)
        user.refresh_from_db()
        self.assertTrue(user.profile.image)

    @vcr.use_cassette('backend_citizen/fixtures/vcr_cassettes/synopsis.yaml')
    def test_google_backend(self):
        class BackendGoogle(object):
            name = 'google-oauth2'
        backend = BackendGoogle()
        user = User.objects.create_user(username="the_user", password=PASSWORD, email='perrito@gmail.com')
        response = {
            'id': 123,
            'image':{
              'url':IMAGE_URL,
              'isDefault':False
           },
        }

        get_image_from_social(backend, None, None, response, user=user)
        user.refresh_from_db()
        self.assertTrue(user.profile.image)