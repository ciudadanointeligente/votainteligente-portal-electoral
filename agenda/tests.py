from elections.tests import VotaInteligenteTestCase as TestCase
from agenda.models import Activity
import datetime
from django.utils import timezone
from elections.models import Candidate
from agenda.forms import ActivityForm
from django.contrib.auth.models import User

tomorrow = timezone.now() + datetime.timedelta(days=1)


class ActivityTestCase(TestCase):
    def setUp(self):
        pass

    def test_instantiate_activity_model(self):
        activity = Activity.objects.create(date=tomorrow,
                                           url='https://perrito.cl/actividad_secreta',
                                           description='This is a description',
                                           location='secret location')
        self.assertTrue(activity)
        self.assertTrue(activity.created)
        self.assertTrue(activity.updated)
        self.assertIsNone(activity.content_type)
        self.assertIsNone(activity.object_id)
        self.assertIsNone(activity.content_object)
        self.assertFalse(activity.background_image)
        self.assertFalse(activity.long_description)

    def test_activity_model_has_image(self):
        image = self.get_image()
        activity = Activity.objects.create(date=tomorrow,
                                           url='https://perrito.cl/actividad_secreta',
                                           description='This is a description',
                                           background_image=image,
                                           location='secret location')
        self.assertTrue(activity.background_image)



class ActivityFormTestCase(TestCase):
    def setUp(self):
        pass

    def test_create_one(self):
        data = {
            'date': tomorrow,
            'url': 'https://perrito.cl/actividad_secreta',
            'description': 'This is a description',
            'location': 'secret location'
        }
        user = User.objects.create_user(username="perrito")
        form = ActivityForm(data=data, content_object=user)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEquals(instance.date, tomorrow)
        self.assertEquals(instance.url, data['url'])
        self.assertEquals(instance.description, data['description'])
        self.assertEquals(instance.location, data['location'])
        self.assertEquals(instance.content_object, user)
