# coding=utf-8
from tse_data_importer.csv_reader import CsvReader
from tse_data_importer.importer import RowsReaderAdapter
from django.conf import settings
from datetime import datetime
from django.core.validators import validate_email
from constance import config
from elections.models import Area, Election, Candidate, PersonalData
from popolo.models import Identifier
from backend_candidate.models import CandidacyContact


validators = {
    'mail': validate_email
}

area_settings = {
    18:'slug',
    17:'area_name',
    23: 'election_name',
}
candidate_settings = {
    0: 'identifier',
    3: 'nome_completo',
    2: 'number',
    6: 'cpf',
    1: 'nome',
    12: 'job',
    5: 'date_of_birth',
    4: 'gender',
    11: 'education',
    8: 'civil_status',
    9: 'race',
    28: 'mail',
    21: 'img',

}
partido_settings = {
    25: 'number',
    27: 'name',
    26: 'initials'
}
coaligacao_settings = {
    22: "name",
    22: "partidos_coaligacao",
    22: "number"

}
settings = {
    'area': area_settings,
    'candidate': candidate_settings,
    'partido': partido_settings,
    'coaligacao': coaligacao_settings
}



class TSEProcessorMixin(object):
    def process_candidate(self, candidate_dict, election, partido_dict, coaligacao_dict, email_repeated):
            # try:
            #     data_de_nascimento = datetime.strptime(candidate_dict['date_of_birth'], "%d/%m/%Y").date()
            # except:
            #     data_de_nascimento = None
            # if Candidate.objects.filter(cpf=candidate_dict['cpf']).exists():
            #     self.output_logger_func("CANDIDATE EXISTENTE DETECTADO CPF:" + candidate_dict['cpf'] + " =====================================>")

            candidate, created = Candidate.objects.get_or_create(name=candidate_dict['nome'])
            candidate.identifiers.add(Identifier.objects.create(identifier=candidate_dict['identifier']))
            candidate.image = candidate_dict['img']
            PersonalData.objects.create(label=u'Partido',
                                        value=partido_dict['initials'],
                                        candidate=candidate)
            PersonalData.objects.create(label=u'Coligação',
                                        value=partido_dict['initials'],
                                        candidate=candidate)
            candidate.save()
            if not email_repeated and candidate_dict['mail'] is not None:
                CandidacyContact.objects.create(candidate=candidate,
                                                mail= candidate_dict['mail'])
            else:
                print u"EMAIL REPETIDO {email} para candidato {candidato} Contato no creado".format(email=candidate_dict['mail'],
                                                                                                    candidato=candidate.name)
            election.candidates.add(candidate)
            return candidate

    def do_something(self, row):
        result = {}
        area = Area.objects.get(id=config.DEFAULT_AREA)
        election, created = area.elections.get_or_create(name=row['area']['election_name'], position=row['area']['election_name'])
        self.process_candidate(row['candidate'], election, row['partido'], row['coaligacao'], row['email_repeated'])
        return result


class TSEProcessor(TSEProcessorMixin, CsvReader):
    settings = settings