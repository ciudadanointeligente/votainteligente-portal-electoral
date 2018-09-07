import numpy as np
from candidator.models import Position
from elections.models import QuestionCategory
from merepresenta.models import Candidate


class MatrixBuilder(object):
    def __init__(self, *args, **kwargs):
        self.positions = Position.objects.all().order_by('id')
        self.candidates = Candidate.objects.filter(candidatequestioncategory__isnull=False).order_by('id')
        self.categories = QuestionCategory.objects.all().order_by('id')
        self.positions_id = self.set_index_of(self.positions)
        self.categories_id = self.set_index_of(self.categories)
        self.candidates_id = self.set_index_of(self.candidates)
        self.electors_categories = np.ones(self.categories.count())
        self.coalicagaos_nota = self.get_coaligacao_marks()

    def set_index_of(self, variable):
        index = 0
        result = {}
        for v in variable:
            result[v.id] = index
            index +=1
        return result
    
    def get_coaligacao_marks(self):
        coalicagaos_nota = np.ones(len(self.candidates_id))
        for c in self.candidates:
            index = self.candidates_id[c.id]
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
        CPR = self.get_candidates_right_positions_matrix()
        return np.dot(CPR, self.electors_categories)

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
            as_array.append({'candidato': c, 'nota': mark})
        return as_array
