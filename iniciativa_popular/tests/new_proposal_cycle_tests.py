# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Area
from django.contrib.auth.models import User
from iniciativa_popular.models import ProposalTemporaryData


class TemporaryDataForPromise(TestCase):
    def setUp(self):
        super(TemporaryDataForPromise, self).setUp()

    def test_instanciate_one(self):
        fiera = User.objects.get(username='fiera')
        arica = Area.objects.get(id='arica-15101')
        data = {
            'your_name': u'Fiera Feroz',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'
        }
        temporary_area = ProposalTemporaryData.objects.create(user=fiera,
                                                              area=arica,
                                                              data=data)
        self.assertTrue(temporary_area)
        self.assertTrue(temporary_area.data['your_name'])
        self.assertFalse(temporary_area.rejected)
        self.assertFalse(temporary_area.rejected_reason)

