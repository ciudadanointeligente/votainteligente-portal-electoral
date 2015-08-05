from django.test import TestCase, override_settings

@override_settings(THEME=None)
class VotaInteligenteTestCase(TestCase):
    fixtures = ['example_data_mini.yaml', 'mini_2.yaml']

    def setUp(self):
        super(VotaInteligenteTestCase, self).setUp()
