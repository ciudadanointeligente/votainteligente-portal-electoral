# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.voluntarios.forms import UpdateAreaForm
from elections.models import Area
from django.contrib.auth.models import User
from merepresenta.voluntarios.models import VolunteerProfile


class UpdateAreaForVolunteerForm(TestCase):
    def setUp(self):
        super(UpdateAreaForVolunteerForm, self).setUp()
        self.area = Area.objects.create(name='area')
        self.volunteer = User.objects.create_user(username='volunteer', is_staff=True)
        self.profile = VolunteerProfile.objects.create(user=self.volunteer)


    def test_instanciate_and_save(self):
        data = {
            'area': self.area.id
        }
        form = UpdateAreaForm(data=data, instance=self.profile)
        self.assertTrue(form.is_valid())
        profile = form.save()

        self.assertEquals(profile.area, self.area)

