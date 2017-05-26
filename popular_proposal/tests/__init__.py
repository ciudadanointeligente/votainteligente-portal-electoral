# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from elections.models import Area


class ProposingCycleTestCaseBase(TestCase):

    def setUp(self):
        super(ProposingCycleTestCaseBase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.feli = User.objects.get(username='feli')
        self.arica = Area.objects.get(id='arica-15101')
        self.alhue = Area.objects.get(id='alhue-13502')
        self.data = {
            'clasification': 'educacion',
            'title': u'Fiera a Santiago',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos\
 y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'causes': u'La super distancia',
            'join_advocacy_url': u'http://ciudadanoi.org',
            'terms_and_conditions': True
        }
        self.comments = {
            'title': '',
            'problem': '',
            'solution': '',
            'when': u'El plazo no está tan bueno',
            'causes': ''
        }
