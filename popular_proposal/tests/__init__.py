# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from popolo.models import Area, Organization


class ProposingCycleTestCaseBase(TestCase):
    def setUp(self):
        super(ProposingCycleTestCaseBase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.feli = User.objects.get(username='feli')
        self.arica = Area.objects.get(id='arica-15101')
        self.data = {
            'clasification': 'genero',
            'title': u'Fiera a Santiago',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'ideal_situation': u'El Feli y el resto de los cabros de la FCI',
            'causes': u'La super distancia'
        }
        self.comments = {
            'title': '',
            'problem': '',
            'solution': '',
            'when': u'El plazo no está tan bueno',
            'ideal_situation': '',
            'causes': ''
        }
