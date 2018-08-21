# coding=utf-8
from merepresenta.tests.volunteers import VolunteersTestCaseBase
from merepresenta.tse_processor import TSEProcessorMixin
from elections.models import Area
from merepresenta.models import Candidate, Partido, Coaligacao
from django.core.management import call_command
from django.conf import settings
from django.test import override_settings


class ImporterTestCase(VolunteersTestCaseBase):
    def setUp(self):
        super(ImporterTestCase, self).setUp()
        self.data = {'partido': {'number': 17, 'name': 'PARTIDO SOCIAL LIBERAL', 'initials': 'PSL'},
                     'coaligacao': {'number': '1', 'name': 'RIO SOLIDoRIO', 'partidos_coaligacao': 'SD / PSL'},
                     'email_repeated': False,
                     'candidate': {'race': 'PARDA', 'nome': 'PARA DO SANTO ALEIXO', 'gender': 'MASCULINO',
                                   'civil_status': 'CASADO(A)', 'number': 1723, 'cpf': 52243184753, 'job': 'APOSENTADO (EXCETO SERVIDOR PoBLICO)',
                                   'date_of_birth': '21/07/1958', 'nome_completo': 'CARLOS ALBERTO HERMoNIO DE MORAES',
                                   'mail': 'candidato@partido.com', 'education': 'ENSINO FUNDAMENTAL COMPLETO'},
                     'area': {'election_name': 'DEPUTADO FEDERAL', 'slug': 'RJ', 'area_name': u"Río de Janeiro"}
                    }

    @override_settings(FILTERABLE_AREAS_TYPE=['state',])
    def test_creates_elements(self):
        rj_area = Area.objects.get(identifier='RJ')

        class JustForNowProcessor(TSEProcessorMixin):
            pass
        processor = JustForNowProcessor()
        result = processor.do_something(self.data)
        area = result['area']
        self.assertEquals(area.id, rj_area.id)
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
        self.assertEquals(candidato.cpf, '52243184753')
        self.assertEquals(candidato.nome_completo, 'CARLOS ALBERTO HERMoNIO DE MORAES')
        self.assertEquals(candidato.numero, 1723)
        self.assertEquals(candidato.gender, 'M')
        self.assertEquals(candidato.race, 'PARDA')
        self.assertEquals(candidato.original_email, 'candidato@partido.com')
        self.assertFalse(candidato.email_repeated)
        self.assertEquals(candidato.partido, partido)
        d = candidato.data_de_nascimento
        self.assertEquals(d.year, 1958)
        self.assertEquals(d.month, 7)
        self.assertEquals(d.day, 21)


    def test_calling_command(self):
        call_command('import_from_tse', './tse_data_importer/fixtures/example_candidates.txt')
        candidate = Candidate.objects.get(name=u'EDUARDO SALLES')
        self.assertTrue(candidate)
        self.assertTrue(candidate.cpf)
        self.assertFalse(candidate.email_repeated)