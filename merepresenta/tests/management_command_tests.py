# coding=utf-8
from merepresenta.tests.volunteers import VolunteersTestCaseBase
from merepresenta.tse_processor import TSEProcessor
from elections.models import Area
from merepresenta.models import Candidate, Partido, Coaligacao


class ImporterTestCase(VolunteersTestCaseBase):
    def setUp(self):
        super(ImporterTestCase, self).setUp()
        self.data = {'partido': {'number': 17, 'name': 'PARTIDO SOCIAL LIBERAL', 'initials': 'PSL'},
                     'coaligacao': {'number': '1', 'name': 'RIO SOLIDoRIO', 'partidos_coaligacao': 'SD / PSL'},
                     'email_repeated': None,
                     'candidate': {'race': 'PARDA', 'nome': 'PARA DO SANTO ALEIXO', 'gender': 'MASCULINO',
                                   'civil_status': 'CASADO(A)', 'number': 1723, 'cpf': 52243184753, 'job': 'APOSENTADO (EXCETO SERVIDOR PoBLICO)',
                                   'date_of_birth': '21/07/1958', 'nome_completo': 'CARLOS ALBERTO HERMoNIO DE MORAES',
                                   'mail': None, 'education': 'ENSINO FUNDAMENTAL COMPLETO'},
                     'area': {'election_name': 'DEPUTADO FEDERAL', 'slug': 'RJ'}
                    }


    def test_creates_elements(self):
        rj_area = Area.objects.get(identifier='RJ')
        processor = TSEProcessor()
        result = processor.do_something(self.data)
        area = result['area']
        self.assertEquals(area, rj_area)
        election = result['election']
        self.assertEquals(election.name, 'DEPUTADO FEDERAL')
        self.assertEquals(election.area, area)
        coaligacao = result['coaligacao']
        self.assertEquals(coaligacao.name, 'RIO SOLIDoRIO')
        self.assertEquals(coaligacao.number, '1')
        partido = result['partido']
        self.assertEquals(partido.name, u'PARTIDO SOCIAL LIBERAL')
        self.assertEquals(partido.initials, u'PSL')
        self.assertEquals(partido.number, 17)
        self.assertEquals(partido.coaligacao, coaligacao)
        candidato = result['candidate']
        self.assertEquals(candidato.election, election)
        self.assertEquals(candidato.name, 'PARA DO SANTO ALEIXO')
        self.assertEquals(candidato.cpf, 52243184753)
        self.assertEquals(candidato.nome_completo, 'CARLOS ALBERTO HERMoNIO DE MORAES')
        self.assertEquals(candidato.numero, 1723)
        self.assertEquals(candidato.gender, 'M')
        self.assertEquals(candidato.partido, partido)

