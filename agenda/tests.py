from django.test import TestCase
from agenda.models import Activity
import datetime
from django.utils import timezone
from elections.models import Candidate


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
