# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Area, Organization
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData


class TemporaryDataForPromise(TestCase):
    def setUp(self):
        super(TemporaryDataForPromise, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.arica = Area.objects.get(id='arica-15101')
        self.data = {
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'
        }

    def test_instanciate_one(self):
        temporary_area = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        self.assertTrue(temporary_area)
        self.assertFalse(temporary_area.rejected)
        self.assertFalse(temporary_area.rejected_reason)
        self.assertIsNotNone(temporary_area.comments['problem'])
        self.assertIsNotNone(temporary_area.comments['solution'])
        self.assertIsNotNone(temporary_area.comments['when'])
        self.assertIsNotNone(temporary_area.comments['allies'])

    def test_proposing_with_an_organization(self):
        local_org = Organization.objects.create(name="Local Organization")
        temporary_area = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              organization=local_org,
                                                              area=self.arica,
                                                              data=self.data)
        self.assertTrue(temporary_area)
        self.assertEquals(temporary_area.organization, local_org)

