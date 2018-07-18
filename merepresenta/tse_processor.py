from elections.models import Area
from merepresenta.models import Partido, Coaligacao, Candidate


class TSEProcessorMixin(object):
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
        result['candidate'] = self.process_candidate(row['candidate'], election, partido)
        return result

class TSEProcessor(TSEProcessorMixin):
    pass