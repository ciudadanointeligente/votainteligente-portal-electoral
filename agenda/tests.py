from elections.tests import VotaInteligenteTestCase as TestCase
from agenda.models import Activity
import datetime
from django.utils import timezone
from elections.models import Candidate
from agenda.forms import ActivityForm
from django.contrib.auth.models import User

tomorrow = timezone.now() + datetime.timedelta(days=1)
two_days_from_now = timezone.now() + datetime.timedelta(days=2)
yesterday = timezone.now() - datetime.timedelta(days=1)


class ActivityTestCase(TestCase):
    def setUp(self):
        pass

    def test_instantiate_activity_model(self):
        activity = Activity.objects.create(date=tomorrow,
                                           url='https://perrito.cl/actividad_secreta',
                                           description='This is a description',
                                           contact_info='the_contact_info',
                                           location='secret location')
        self.assertTrue(activity)
        self.assertTrue(activity.created)
        self.assertTrue(activity.updated)
        self.assertIsNone(activity.content_type)
        self.assertIsNone(activity.object_id)
        self.assertIsNone(activity.content_object)
        self.assertFalse(activity.background_image)
        self.assertFalse(activity.long_description)
        self.assertFalse(activity.important)

    def test_location_is_optional(self):
        activity = Activity.objects.create(date=tomorrow,
                                           url='https://perrito.cl/actividad_secreta',
                                           description='This is a description',
                                           contact_info='the_contact_info')
        self.assertTrue(activity)
        self.assertFalse(activity.location)

    def test_activity_model_has_image(self):
        image = self.get_image()
        activity = Activity.objects.create(date=tomorrow,
                                           url='https://perrito.cl/actividad_secreta',
                                           description='This is a description',
                                           background_image=image,
                                           location='secret location')
        self.assertTrue(activity.background_image)

    def test_future_activities_manager(self):
        activity1 = Activity.objects.create(date=yesterday,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='yesterdays activity',
                                            location='secret location')
        activity2 = Activity.objects.create(date=tomorrow,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='tomorrows activity',
                                            location='secret location')
        activity3 = Activity.objects.create(date=two_days_from_now,
                                            url='https://perrito.cl/actividad_secreta',
                                            description='this activity is in two days',
                                            location='secret location')
        future_activities = Activity.futures.all()
        self.assertNotIn(activity1, future_activities)
        self.assertIn(activity2, future_activities)
        self.assertIn(activity3, future_activities)


class ActivityFormTestCase(TestCase):
    def setUp(self):
        pass

    def test_create_one(self):
        data = {
            'date': tomorrow,
            'url': 'https://perrito.cl/actividad_secreta',
            'description': 'This is a description',
            'location': 'secret location',
            'contact_info': 'telefono y email',
        }
        user = User.objects.create_user(username="perrito")
        form = ActivityForm(data=data, content_object=user)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEquals(instance.date, tomorrow)
        self.assertEquals(instance.url, data['url'])
        self.assertEquals(instance.description, data['description'])
        self.assertEquals(instance.location, data['location'])
        self.assertEquals(instance.contact_info, data['contact_info'])
        self.assertEquals(instance.content_object, user)
