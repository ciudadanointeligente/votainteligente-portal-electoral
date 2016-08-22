from django.test import TestCase, override_settings
from PIL import Image
from StringIO import StringIO
from django.core.files.base import ContentFile
import random
import os
__dir__ = os.path.dirname(os.path.realpath(__file__))


@override_settings(THEME=None)
class VotaInteligenteTestCase(TestCase):
    fixtures = ['mini_2.yaml']

    def setUp(self):
        super(VotaInteligenteTestCase, self).setUp()

    def get_image(self):
        image_file = StringIO()
        color1 = random.randint(0, 255)
        color2 = random.randint(0, 255)
        color3 = random.randint(0, 255)
        image = Image.new('RGBA', size=(50, 50), color=(color1, color2, color3))
        image.save(image_file, 'png')
        image_file.seek(0)
        return ContentFile(image_file.read(), 'test.png')

    def get_document(self):
        pdf_file = open(__dir__ + '/fixtures/example.pdf')
        return ContentFile(pdf_file.read(), 'example.pdf')