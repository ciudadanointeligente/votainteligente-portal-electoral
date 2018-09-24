import numpy as np
from candidator.models import Position
from elections.models import QuestionCategory
from merepresenta.models import Candidate
from django.core.cache import cache
from constance import config


class InformationHolder(object):
    def __init__(self, positions, candidates, categories):
        self.positions = positions
        self.candidates = candidates
        self.categories = categories

        self.positions_id = self.set_index_of(positions)
        self.categories_id = self.set_index_of(categories)
        self.candidates_id = self.set_index_of(candidates)
        self.electors_categories = np.ones(categories.count())
        self.coalicagaos_nota = self.get_coaligacao_marks(self.candidates_id, candidates)
        self.candidates_dict = self.get_candidates_dict(candidates)
        self.desprivilegios = self.get_desprivilegios(candidates)

    def as_tuple(self):
        return (self.positions, 
                self.candidates, 
                self.categories, 
                self.positions_id, 
                self.categories_id, 
                self.candidates_id, 
                self.electors_categories, 
                self.coalicagaos_nota, 
                self.candidates_dict, 
                self.desprivilegios)

    def set_index_of(self, variable):
        index = 0
        result = {}
        for v in variable:
            result[v.id] = index
            index +=1
        return result

    def get_candidates_dict(self, candidates):
        candidates_dict = {}
        for c in candidates:
            candidates_dict[c.id] = c.as_dict()
        return candidates_dict

    def get_desprivilegios(self, candidates):
        r = np.zeros(len(candidates))
        counter = 0
        for c in candidates:
            r[counter] = c.desprivilegio
            counter += 1
        return r
    
    def get_coaligacao_marks(self, candidates_id, candidates):
        coalicagaos_nota = np.ones(len(candidates))
        for c in candidates:
            index = candidates_id[c.id]
            try:
                mark = c.partido.coaligacao.mark
                coalicagaos_nota[index] = mark
            except:
                pass
        return coalicagaos_nota


class CandidatesRightPositionsVector(object):
    def __init__(self, information_holder):
        self.information_holder = information_holder
        self.right_candidates_positions_vector = self.get_candidates_right_positions_matrix()

    def as_tuple(self):
        return self.information_holder.as_tuple() + (self.right_candidates_positions_vector, )

    def get_positions_vector_for_category(self, cat):
        result = np.zeros(self.information_holder.positions.count())
        for topic in cat.topics.all():
            i = self.information_holder.positions_id[topic.right_answer.position.id]
            result[i] = 1
        return result

    def get_matrix_positions_and_categories(self):
        r = []
        for c in self.information_holder.categories:
            r.append(self.get_positions_vector_for_category(c))
        return np.vstack(r).T

    def get_positions_vector_for_candidate(self, cand):
        r = np.zeros(self.information_holder.positions.count())
        for p in self.information_holder.positions:
            if cand.candidatequestioncategory_set.filter(category=p.topic.category).exists():
                multiplier = 2
            else:
                multiplier = 1
            if cand.taken_positions.filter(position=p).exists():
                index = self.information_holder.positions_id[p.id]
                r[index] = 1 * multiplier
        return r.T

    def get_matrix_positions_and_candidates(self):
        r = []
        for c in self.information_holder.candidates:
            r.append(self.get_positions_vector_for_candidate(c))
        return np.vstack(r)

    def get_candidates_right_positions_matrix(self):

        C = self.get_matrix_positions_and_candidates()
        P = self.get_matrix_positions_and_categories()
        return np.dot(C ,P)



class MatrixBuilder(object):
    cache_key = 'merepresenta_matrix_builder_setup_b'
    def __init__(self, *args, **kwargs):
        self.cache_time = kwargs.pop('time', 83600)
        if cache.get(self.cache_key) is None:
            all_ = self.set_cache()
        else:
            all_ = cache.get(self.cache_key)

        (self.positions,
        self.candidates,
        self.categories,
        self.positions_id,
        self.categories_id,
        self.candidates_id,
        self.electors_categories,
        self.coalicagaos_nota,
        self.candidates_dict,
        self.desprivilegios,
        self.right_candidates_positions) = all_
        

    def set_cache(self):
        positions = Position.objects.all().order_by('id')
        candidates = Candidate.objects.filter(candidatequestioncategory__isnull=False).order_by('id').distinct()
        categories = QuestionCategory.objects.all().order_by('id')
        information_holder = InformationHolder(positions, candidates, categories)
        right_candidates_positions_vector = CandidatesRightPositionsVector(information_holder)
        all_ = right_candidates_positions_vector.as_tuple()
        cache.set(self.cache_key, all_, self.cache_time)
        return all_

    def set_electors_categories(self, categories):
        for c in categories:
            index = self.categories_id[c.id]
            self.electors_categories[index] = 3

    def get_candidates_result(self):
        # Candidates right answers multiplied by 2 if she chooses
        # the given TEMA
        CPR = self.right_candidates_positions
        result = np.dot(CPR, self.electors_categories)
        result = result + self.desprivilegios * config.MEREPRESENTA_IDENTITY_MULTIPLICATION_FACTOR
        return result

    def get_result(self):
        C = self.get_candidates_result()
        notas = self.coalicagaos_nota.T
        notas = notas * config.MEREPRESENTA_COLIGACAO_ATENUATION_FACTOR
        return C * notas

    def get_result_as_array(self):
        r = self.get_result()
        as_array = []
        index = 0
        for c in self.candidates:
            i = self.candidates_id[c.id]
            mark = r[i]
            d = self.candidates_dict[c.id]
            d['nota'] = round(float(mark)/float(100), 2)
            as_array.append(d)
        return as_array
