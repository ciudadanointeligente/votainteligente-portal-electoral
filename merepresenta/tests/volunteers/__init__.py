# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import PersonalData
from merepresenta.models import Candidate, NON_WHITE_KEY, NON_MALE_KEY

class VolunteersTestCaseBase(TestCase):
    fixtures = ['merep_mini.yaml', 'estados_de_brasil.yaml']
    def set_desprivilegios_on_candidates(self):
        Candidate.objects.filter(id__in=[4, 5]).update(gender=NON_MALE_KEY)
        c = Candidate.objects.get(id=5)
        personal_data = PersonalData.objects.create(label=u'Cor e raça',
                                                    value=NON_WHITE_KEY["possible_values"][0],
                                                    candidate=c)
