# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.core.urlresolvers import reverse
from agenda.forms import ActivityForm
from django.contrib.auth.models import User
import datetime
from agenda.models import Activity
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from elections.models import Candidate


PASSWORD = u'PASSWORD'
TOMORROW = timezone.now() + datetime.timedelta(days=1)
IN_TWO_DAYS = timezone.now() + datetime.timedelta(days=2)
IN_THREE_DAYS = timezone.now() + datetime.timedelta(days=3)


class AgendaCitizenViewTestCase(TestCase):
    def setUp(self):
        self.feli = User.objects.get(username=u'feli')
        self.feli.set_password(PASSWORD)
        self.feli.save()
        self.image = self.get_image()

    def test_get_create_an_activity_from_view(self):
        url = reverse('backend_citizen:add_activity')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        self.client.login(username=self.feli,
                          password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_citizen/add_activity.html')
        form = response.context['form']
        self.assertIsInstance(form, ActivityForm)

    def test_post_create_an_activity(self):
        url = reverse('backend_citizen:add_activity')
        data = {
            'date': TOMORROW.strftime('%Y-%m-%d %H:%M:%S'),
            'url': 'https://perrito.cl/actividad_secreta',
            'description': 'This is a description',
            'location': 'secret location',
            'background_image': self.image
        }
        self.client.login(username=self.feli,
                          password=PASSWORD)
        response = self.client.post(url, data)
        all_my_activities_url = reverse('backend_citizen:all_my_activities')
        self.assertRedirects(response, all_my_activities_url)
        content_type = ContentType.objects.get_for_model(self.feli)
        activity = Activity.objects.get(object_id=self.feli.id,
                                        content_type=content_type)

    def test_list_all_my_activities(self):
        other_user = User.objects.create_user(username='other')
        activity1 = Activity.objects.create(date=TOMORROW,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='This is a description',
                                            content_object=other_user,
                                            location='secret location')

        activity2 = Activity.objects.create(date=TOMORROW,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='This is a description',
                                            content_object=self.feli,
                                            location='secret location')
        activity3 = Activity.objects.create(date=TOMORROW,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='This is a description',
                                            content_object=self.feli,
                                            location='secret location')
        url = reverse('backend_citizen:all_my_activities')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        self.client.login(username=self.feli,
                          password=PASSWORD)

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_citizen/all_my_activities.html')
        activities = response.context['activities']
        self.assertIn(activity2, activities)
        self.assertIn(activity3, activities)
        self.assertNotIn(activity1, activities)

    def test_list_public_events(self):
        other_user = User.objects.create_user(username='other')
        activity1 = Activity.objects.create(date=IN_THREE_DAYS,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='This is a description',
                                            content_object=other_user,
                                            location='secret location')
        activity2 = Activity.objects.create(date=IN_TWO_DAYS,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='This is a description',
                                            content_object=self.feli,
                                            location='secret location')
        activity3 = Activity.objects.create(date=TOMORROW,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='This is a description',
                                            content_object=self.feli,
                                            location='secret location')
        candidate = Candidate.objects.get(pk=1)
        candidate_activity = Activity.objects.create(date=TOMORROW,
                                                     url='https://perrito.cl/actividad_secreta',
                                                     description='This is a description',
                                                     content_object=candidate,
                                                     location='secret location')
        url = reverse('backend_citizen:all_activities')
        response = self.client.get(url)
        activities = response.context['activities']
        self.assertNotIn(candidate_activity, activities)
        self.assertIn(activity1, activities)
        self.assertIn(activity2, activities)
        self.assertIn(activity3, activities)
