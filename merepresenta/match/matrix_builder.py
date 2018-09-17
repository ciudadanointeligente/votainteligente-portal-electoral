import numpy as np
from candidator.models import Position
from elections.models import QuestionCategory
from merepresenta.models import Candidate
from django.core.cache import cache


class MatrixBuilder(object):
    cache_key_candidates_right_positions = 'candidates_right_positions'
    cache_key = 'merepresenta_matrix_builder_setup_'
    def __init__(self, *args, **kwargs):
        
        self.cache_time = kwargs.pop('time', 6000)
        if cache.get(self.cache_key) is None:
            positions = Position.objects.all().order_by('id')
            candidates = Candidate.objects.filter(candidatequestioncategory__isnull=False).order_by('id').distinct()
            categories = QuestionCategory.objects.all().order_by('id')
            positions_id = self.set_index_of(positions)
            categories_id = self.set_index_of(categories)
            candidates_id = self.set_index_of(candidates)
            electors_categories = np.ones(categories.count())
            coalicagaos_nota = self.get_coaligacao_marks(candidates_id, candidates)
            candidates_dict = self.get_candidates_dict(candidates)
            desprivilegios = self.get_desprivilegios(candidates)
            all_ = (positions,
                    candidates,
                    categories,
                    positions_id,
                    categories_id,
                    candidates_id,
                    electors_categories,
                    coalicagaos_nota,
                    candidates_dict,
                    desprivilegios
                    )
            cache.set(self.cache_key, all_, self.cache_time)
        else:
            all_ = cache.get(self.cache_key)

        self.positions, self.candidates, self.categories, self.positions_id, self.categories_id, self.candidates_id, self.electors_categories, self.coalicagaos_nota, self.candidates_dict, self.desprivilegios = all_

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

    def set_index_of(self, variable):
        index = 0
        result = {}
        for v in variable:
            result[v.id] = index
            index +=1
        return result
    
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

    def get_positions_vector_for_category(self, cat):
        result = np.zeros(self.positions.count())
        for topic in cat.topics.all():
            i = self.positions_id[topic.right_answer.position.id]
            result[i] = 1
        return result

    def get_matrix_positions_and_categories(self):
        r = []
        for c in self.categories:
            r.append(self.get_positions_vector_for_category(c))
        return np.vstack(r).T

    def get_positions_vector_for_candidate(self, cand):
        r = np.zeros(self.positions.count())
        for p in self.positions:
            if cand.candidatequestioncategory_set.filter(category=p.topic.category).exists():
                multiplier = 2
            else:
                multiplier = 1
            if cand.taken_positions.filter(position=p).exists():
                index = self.positions_id[p.id]
                r[index] = 1 * multiplier
        return r.T

    def get_matrix_positions_and_candidates(self):
        r = []
        for c in self.candidates:
            r.append(self.get_positions_vector_for_candidate(c))
        return np.vstack(r)

    def get_candidates_right_positions_matrix(self):

        C = self.get_matrix_positions_and_candidates()
        P = self.get_matrix_positions_and_categories()
        return np.dot(C ,P)

    def set_electors_categories(self, categories):
        for c in categories:
            index = self.categories_id[c.id]
            self.electors_categories[index] = 3

    def get_candidates_result(self):
        # Candidates right answers multiplied by 2 if she chooses
        # the given TEMA
        if cache.get(self.cache_key_candidates_right_positions) is None:
            CPR = self.get_candidates_right_positions_matrix()
            cache.set(self.cache_key_candidates_right_positions, CPR, self.cache_time)
        else:
            CPR = cache.get(self.cache_key_candidates_right_positions)
        result = np.dot(CPR, self.electors_categories)
        result = result + self.desprivilegios
        return result

    def get_result(self):
        C = self.get_candidates_result()
        notas = self.coalicagaos_nota.T
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
