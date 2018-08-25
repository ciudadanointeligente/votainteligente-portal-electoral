# coding=utf-8
from elections.models import Area
from merepresenta.models import Partido, Coaligacao, Candidate
from tse_data_importer.csv_reader import CsvReader
from tse_data_importer.importer import RowsReaderAdapter
from django.conf import settings
from datetime import datetime

def output_logger(self, msg):
    print msg

RACE_MAPPING = {
    u'INDÍGENA': u'indigena',
    u'BRANCA': u'branca',
    u'PRETA': u'preta',
    u'PARDA': u'parda',
    u'AMARELA': u'amarela'
}

def try_parsing_date(text):
    ### Me lo traje de stackoverflow
    ### https://stackoverflow.com/questions/23581128/how-to-format-date-string-via-multiple-formats-in-python
    ### Me pareció hacky e ingenioso
    ### Incluso el raise es lindo
    for fmt in ( "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

class TSEProcessorMixin(object):
    output_logger_func = output_logger

    def gender_definer(self, gender):
        if gender in ['FEMININO', 'FEM.']:
            return "F"
        if gender in ['MASCULINO', 'MASC.']:
            return "M"
        return ""

    def process_candidate(self, candidate_dict, election, partido):
        gender = self.gender_definer(candidate_dict['gender'])
        try:
            d = candidate_dict['date_of_birth']
            data_de_nascimento = try_parsing_date(d)
            data_de_nascimento = data_de_nascimento.date()
        except:
            data_de_nascimento = None
        cpf = unicode(int(candidate_dict['cpf']))
        if Candidate.objects.filter(cpf=cpf).exists():
            self.output_logger_func("CANDIDATE EXISTENTE DETECTADO CPF:" + cpf + " =====================================>")
            return Candidate.objects.get(cpf=cpf)
        candidate, created = Candidate.objects.get_or_create(name=candidate_dict['nome'], cpf=cpf)
        candidate.nome_completo = candidate_dict['nome_completo']
        candidate.numero = candidate_dict['number']
        candidate.cpf = cpf
        candidate.data_de_nascimento = data_de_nascimento
        candidate.race = candidate_dict['race']
        if candidate.race in RACE_MAPPING.keys():
            setattr(candidate, RACE_MAPPING[candidate.race], True)
        candidate.original_email = candidate_dict['mail']
        candidate.email_repeated = candidate_dict['email_repeated']
        candidate.partido = partido
        candidate.gender = gender
        candidate.slug = candidate.id
        candidate.save()
        # candidate, created = Candidate.objects.get_or_create(name=candidate_dict['nome'],
        #                                                      nome_completo=candidate_dict['nome_completo'],
        #                                                      numero=candidate_dict['number'],
        #                                                      cpf=candidate_dict['cpf'],
        #                                                      data_de_nascimento=data_de_nascimento,
        #                                                      race=candidate_dict['race'],
        #                                                      original_email=candidate_dict['mail'],
        #                                                      email_repeated=candidate_dict['email_repeated'],
        #                                                      partido = partido,
        #                                                      gender=gender)
        election.candidates.add(candidate)

        return candidate

    def do_something(self, row):
        result = {}
        if settings.FILTERABLE_AREAS_TYPE:
            state_classification = settings.FILTERABLE_AREAS_TYPE[0]
        else:
            state_classification = 'state'
        area, created = Area.objects.get_or_create(identifier=row['area']['slug'], name=row['area']['area_name'], classification=state_classification)
        result['area'] = area
        election, created = area.elections.get_or_create(name=row['area']['election_name'])
        result['election'] = election
        name = row['coaligacao'].get('name', '')
        if not name:
            name = row['coaligacao'].get('number', '')
        number = row['coaligacao'].get('number', 0)

        coaligacao, created = Coaligacao.objects.get_or_create(name=name,
                                                               number=number)
        result['coaligacao'] = coaligacao
        partido, created = Partido.objects.get_or_create(name=row['partido']['name'],
                                                         initials=row['partido']['initials'],
                                                         number=row['partido']['number'],
                                                         coaligacao=coaligacao)
        result['partido'] = partido
        row['candidate']['email_repeated'] = row['email_repeated']

        result['candidate'] = self.process_candidate(row['candidate'], election, partido)
        self.output_logger_func("imported %s de %s" % (result['candidate'].name, area.name))
        return result

class TSEProcessor(TSEProcessorMixin, CsvReader):
    pass