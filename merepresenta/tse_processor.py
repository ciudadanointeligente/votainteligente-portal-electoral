# coding=utf-8
from elections.models import Area
from merepresenta.models import Partido, Coaligacao, Candidate
from tse_data_importer.csv_reader import CsvReader
from tse_data_importer.importer import RowsReaderAdapter

def output_logger(self, msg):
    print msg

class TSEProcessorMixin(object):
    output_logger_func = output_logger

    def gender_definer(self, gender):
        if gender == 'FEMININO':
            return "F"
        if gender == 'MASCULINO':
            return "M"
        return ""

    def process_candidate(self, candidate_dict, election, partido):
        gender = self.gender_definer(candidate_dict['gender'])

        candidate, created = Candidate.objects.get_or_create(name=candidate_dict['nome'],
                                                             nome_completo=candidate_dict['nome_completo'],
                                                             numero=candidate_dict['number'],
                                                             cpf=candidate_dict['cpf'],
                                                             race=candidate_dict['race'],
                                                             original_email=candidate_dict['mail'],
                                                             email_repeated=candidate_dict['email_repeated'],
                                                             gender=gender)
        election.candidates.add(candidate)
        candidate.partido = partido
        candidate.save()

        return candidate

    def do_something(self, row):
        
        result = {}
        area, created = Area.objects.get_or_create(identifier=row['area']['slug'])
        result['area'] = area
        election, created = area.elections.get_or_create(name=row['area']['election_name'])
        result['election'] = election
        coaligacao, created = Coaligacao.objects.get_or_create(name=row['coaligacao']['name'],
                                                               number=row['coaligacao']['number'])
        result['coaligacao'] = coaligacao
        partido, created = Partido.objects.get_or_create(name=row['partido']['name'],
                                                         initials=row['partido']['initials'],
                                                         number=row['partido']['number'],
                                                         coaligacao=coaligacao)
        result['partido'] = partido
        row['candidate']['email_repeated'] = row['email_repeated']

        result['candidate'] = self.process_candidate(row['candidate'], election, partido)
        self.output_logger_func(result['candidate'].name)
        return result

class TSEProcessor(TSEProcessorMixin, CsvReader):
    pass