from django.test import TestCase
from django.test import override_settings
from django.core.urlresolvers import reverse


@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class StandAloneSite(TestCase):
    def test_get_index(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
