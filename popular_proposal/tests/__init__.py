# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from elections.models import Area
from popular_proposal.forms.forms import wizard_forms_fields
from django import forms

example_fields = {
    'CharField': 'fieraFeroz',
    'URLField': 'http://fieraFeroz.com',
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

class ProposingCycleTestCaseBase(TestCase):

    def setUp(self):
        super(ProposingCycleTestCaseBase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.feli = User.objects.get(username='feli')
        self.arica = Area.objects.get(id=3)
        self.alhue = Area.objects.get(id=2)
        self.data = get_example_data_for_testing()
        self.comments = {
            'title': '',
            'problem': '',
            'when': u'El plazo no está tan bueno',
            'causes': ''
        }
