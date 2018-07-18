# coding=utf-8
from django.test import TestCase
from tse_data_importer.importer import RowReader, MultipleRowsReader, RowsReaderAdapter
from tse_data_importer.csv_reader import CsvReader

row_1 = ["17/05/2018","04:01:20",2014,1,"Eleicoes Gerais 2014","RJ","RJ","RIO DE JANEIRO",7,"DEPUTADO ESTADUAL",
         "EDUARDO SALLES DE ARAúJO JUNIOR",190000000560,13318,4768296742,"EDUARDO SALLES",2,"DEFERIDO",13,"PT",
         "PARTIDO DOS TRABALHADORES",190000000010,"#NULO#","PT","PARTIDO ISOLADO",257,"EMPRESaRIO","18/03/1978",110595560345,
         36,2,"MASCULINO",8,"SUPERIOR COMPLETO",3,"CASADO(A)",1,"BRANCA",1,"BRASILEIRA NATA","RJ",-3,"RIO DE JANEIRO",3000000,5,
         "SUPLENTE","perrito@gatito.com"]

row_2 = ["17/05/2018","04:01:20",2014,1,"Eleiooes Gerais 2014","RJ","RJ","RIO DE JANEIRO",6,"DEPUTADO FEDERAL","CARLOS ALBERTO HERMoNIO DE MORAES",
         190000000343,1723,52243184753,"PARA DO SANTO ALEIXO",2,"DEFERIDO",17,"PSL","PARTIDO SOCIAL LIBERAL",190000000007,"#NULO#",
         "SD / PSL","RIO SOLIDoRIO",923,"APOSENTADO (EXCETO SERVIDOR PoBLICO)",
         "21/07/1958",66895110310,56,2,"MASCULINO",4,"ENSINO FUNDAMENTAL COMPLETO",3,"CASADO(A)",3,"PARDA",1,
         "BRASILEIRA NATA","RJ",-3,"MAGE",5000000,5,"SUPLENTE","#NULO#"]

row_3 = ["17/05/2018","04:01:20",2014,1,"Eleiooes Gerais 2014","RJ","RJ","RIO DE JANEIRO",6,"DEPUTADO FEDERAL","ALCEU ALVES BARBOSA JUNIOR",
         190000000682,7097,688960774,"ALCEU JUNIOR",2,"DEFERIDO",70,"PT do B","PARTIDO TRABALHISTA DO BRASIL",190000000015,"#NULO#","PT do B",
         "PARTIDO ISOLADO",169,"COMERCIANTE","15/11/1970",75667840337,43,2,"MASCULINO",6,"ENSINO MoDIO COMPLETO",3,"CASADO(A)",1,"BRANCA",1,
         "BRASILEIRA NATA","RJ",-3,"RIO DE JANEIRO",2000000,4,"NoO ELEITO","perrito@gatito.com"]
row_4 = ["17/05/2018","04:01:20",2014,1,"Eleiooes Gerais 2014","RJ","RJ","RIO DE JANEIRO",6,"DEPUTADO FEDERAL","ALCEU ALVES BARBOSA JUNIOR",
         190000000682,7097,688960774,"ALCEU JUNIOR",2,"DEFERIDO",70,"PT do B","PARTIDO TRABALHISTA DO BRASIL",190000000015,"#NULO#","PT do B",
         "PARTIDO ISOLADO",169,"COMERCIANTE","15/11/1970",75667840337,43,2,"MASCULINO",6,"ENSINO MoDIO COMPLETO",3,"CASADO(A)",1,"BRANCA",1,
         "BRASILEIRA NATA","RJ",-3,"RIO DE JANEIRO",2000000,4,"NoO ELEITO","otro_mail@gatito.com"]
row_5 = ["17/05/2018","04:01:20",2014,1,"Eleiooes Gerais 2014","RJ","RJ","RIO DE JANEIRO",6,"DEPUTADO FEDERAL","ALCEU ALVES BARBOSA JUNIOR",
         190000000682,7097,688960774,"ALCEU JUNIOR",2,"DEFERIDO",70,"PT do B","PARTIDO TRABALHISTA DO BRASIL",190000000015,"#NULO#","PT do B",
         "PARTIDO ISOLADO",169,"COMERCIANTE","15/11/1970",75667840337,43,2,"MASCULINO",6,"ENSINO MoDIO COMPLETO",3,"CASADO(A)",1,"BRANCA",1,
         "BRASILEIRA NATA","RJ",-3,"RIO DE JANEIRO",2000000,4,"NoO ELEITO","otro_mail2@gatito.com"]
all_rows = [row_1, row_2, row_3, row_4, row_5]


area_settings = {
    5:'slug',
    9: 'election_name',
}
candidate_settings = {
    
    10: 'nome_completo',
    12: 'number',
    13: 'cpf',
    14: 'nome',
    25: 'job',
    26: 'date_of_birth',
    30: 'gender',
    32: 'education',
    34: 'civil_status',
    36: 'race',
    45: 'mail',

}
partido_settings = {
    17: 'number',
    19: 'name',
    18: 'initials'
}
coaligacao_settings = {
    23: "name",
    22: "partidos_coaligacao",
    21: "number"

}
settings = {
    'area': area_settings,
    'candidate': candidate_settings,
    'partido': partido_settings,
    'coaligacao': coaligacao_settings
}
class ImporterTestCase(TestCase):
    def test_proces_one_row(self):
        imp = RowReader(row_1, settings=settings)
        result = imp.process()
        candidate_dict = result['candidate']
        self.assertEquals(candidate_dict['mail'], "perrito@gatito.com")
        self.assertEquals(candidate_dict['nome'], 'EDUARDO SALLES')
        self.assertEquals(candidate_dict['nome_completo'], 'EDUARDO SALLES DE ARAúJO JUNIOR')
        self.assertEquals(candidate_dict['cpf'], 4768296742)
        self.assertEquals(candidate_dict['gender'], 'MASCULINO')
        self.assertEquals(candidate_dict['race'], 'BRANCA')
        area_dict = result['area']
        self.assertEquals(area_dict['slug'], 'RJ')
        self.assertEquals(area_dict['election_name'], 'DEPUTADO ESTADUAL')
        self.assertIn('coaligacao', result)
        self.assertIn('partido', result)


    def test_process_one_row_validating_email(self):
        imp = RowReader(row_2, settings=settings)
        result = imp.process()
        candidate_dict = result['candidate']
        self.assertIsNone(candidate_dict['mail'])

    def test_process_multiple_rows(self):
        proc = MultipleRowsReader(all_rows, settings=settings)
        result = proc.process()
        self.assertEquals(len(result), 5)
        first_ = result[0]
        self.assertIn('candidate', first_)
        self.assertIn('area', first_)
        self.assertIn('coaligacao', first_)
        self.assertIn('partido', first_)

    def test_post_process_thing(self):
        proc = MultipleRowsReader(all_rows, settings=settings)
        result = proc.process()

        first_ = result[0]
        second_ = result[1]
        third_ = result[2]
        fourth_ = result[3]
        fifth_ = result[3]

        self.assertIsNone(second_['email_repeated'])
        self.assertTrue(third_['email_repeated'])
        self.assertTrue(first_['email_repeated'])
        self.assertFalse(fourth_['email_repeated'])
        self.assertFalse(fifth_['email_repeated'])
        self.fail()

    def test_management_command_mixin(self):
        class DoSomethingWithEachRow(RowsReaderAdapter):
            def __init__(self, *args, **kwargs):
                super(DoSomethingWithEachRow, self).__init__(*args, **kwargs)
                self.rows_count = 0

            def do_something(self, row):
                self.rows_count += 1
        reader = DoSomethingWithEachRow(all_rows, settings=settings)
        reader.process()
        self.assertEquals(reader.rows_count, 5)

    def test_csv_reader_from_file(self):
        filename = './tse_data_importer/fixtures/example_candidates.txt'
        class ReaderForJustThisTest(CsvReader):
            pass
        reader = ReaderForJustThisTest(filename)
        self.assertEquals(len(reader.rows), 11)
        self.assertGreater(len(reader.rows[0]), 1)