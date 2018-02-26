# coding=utf-8
from django.test import TestCase, override_settings
from django.contrib.auth.models import User

from popular_proposal.forms.forms import wizard_forms_fields
from django import forms
from PIL import Image
from StringIO import StringIO
from django.core.files.base import ContentFile
import random
import os
__dir__ = os.path.dirname(os.path.realpath(__file__))

example_fields = {
    'CharField': u'fieraFeroz',
    'URLField': u'http://fieraFeroz.com',
    'BooleanField': True,
}

def get_example_data_for_testing():
    data = {}

    for step in wizard_forms_fields:
        for f in step['fields']:
            if f == "is_testing":
                data[f] = False
                continue
            field = step['fields'][f]
            field_type = field.__class__.__name__
            if field_type in example_fields:
                data[f] = example_fields[field_type]
            elif field_type == 'ChoiceField':
                data[f] = field.choices[-1][0]
    return data


@override_settings(THEME=None)
class ProposalsTestCase(TestCase):
    fixtures = ['mini_2.yaml']

    def setUp(self):
        super(ProposalsTestCase, self).setUp()

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


class ProposingCycleTestCaseBase(ProposalsTestCase):

    def setUp(self):
        super(ProposingCycleTestCaseBase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.feli = User.objects.get(username='feli')
        self.data = get_example_data_for_testing()
        self.comments = {
            'title': '',
            'problem': '',
            'when': u'El plazo no está tan bueno',
            'causes': ''
        }


