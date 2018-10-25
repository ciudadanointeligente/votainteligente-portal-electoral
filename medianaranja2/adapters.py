from numpy import matrix, ones, zeros
from constance import config
from django.core.cache import cache
from django.conf import settings
from medianaranja2.candidate_proposals_matrix_generator import CandidateCommitmentsMatrixGenerator


class CandidateGetterFromElectionMixin(object):
    @classmethod
    def get_candidates_from_election(cls, election):
        return election.candidates.order_by('id').only('id')

    @classmethod
    def get_candidates_from_election_as_list(cls, election, time=83600):
        cache_key = 'candidates_for_' + str(election.id)
        if cache.get(cache_key) is not None:
            candidates = cache.get(cache_key)
        else:
            candidates = list(cls.get_candidates_from_election(election))
            cache.set(cache_key, candidates, time)
        return candidates

class Adapter(CandidateGetterFromElectionMixin):
    def __init__(self, election, positions):
        self.user_positions = positions
        self.user_questions = []
        for position in self.user_positions:
            if position.topic not in self.user_questions:
                self.user_questions.append(position.topic)
        self.candidates = self.__class__.get_candidates_from_election_as_list(election)
        self.topics, self.positions = self.get_topics_and_positions(election)

    def _get_topics_and_positions(self, election):
        topics = []
        positions = []
        for category in election.categories.all().order_by('id'):
            for topic in category.topics.all().order_by('id'):
                topics.append(topic)
                for position in topic.positions.all().order_by('id'):
                    positions.append(position)
        return (topics, positions)

    def get_topics_and_positions(self, election):
        cache_key = 'topics_and_positions_' + str(election.id)
        if cache.get(cache_key) is not None:
            return cache.get(cache_key)
        topics, positions = self._get_topics_and_positions(election)
        cache.set(cache_key, (topics, positions))
        return (topics, positions)

    def get_responses_vector(self):
        response = []
        for position in self.user_positions:
            topic = position.topic
            for p in topic.positions.all().order_by('id'):
                if p == position:
                    response.append(1)
                else:
                    response.append(0)
        return response

    def get_positions_from_candidate(self, candidate):
        positions = []
        for question in self.user_questions:
            positions_from_question_cache_key = 'positions_from_question_' + str(question.id)
            positions_from_question = cache.get(positions_from_question_cache_key)
            if positions_from_question is None:
                positions_from_question = question.positions.order_by('id')
                cache.set(positions_from_question_cache_key, positions_from_question)
            for position in positions_from_question:
                taken_position_key = u"taken_position_" + str(candidate.id) + u"-" + str(position.id)
                yes_or_no = cache.get(taken_position_key)
                if yes_or_no is None:
                    yes_or_no = None
                    if question.taken_positions.filter(person=candidate, position=position):
                        yes_or_no = 1
                    else:
                        yes_or_no = 0
                    cache.set(taken_position_key, yes_or_no)
                positions.append(yes_or_no)
        return positions

    def get_responses_matrix(self):
        matrix = []
        for candidate in self.candidates:
            matrix.append(self.get_positions_from_candidate(candidate))
        return matrix


class CommitmentsAdapter(CandidateGetterFromElectionMixin):
    def __init__(self, election, proposals):
        self.candidates = CommitmentsAdapter.get_candidates_from_election_as_list(election)
        self.proposals = proposals
        self.ones = ones((len(self.proposals),1))
        matrix_generator = CandidateCommitmentsMatrixGenerator()
        self.all_candidates_and_proposals = matrix_generator.get_matrix_with_all_proposals()
        self.candidate_index_in_matrix = matrix_generator._get_candidate_index_in_matrix()
        self.proposal_index_in_matrix = matrix_generator._get_proposal_index_in_matrix()

    def get_commitments_matrix(self):
        _C = []
        for candidate in self.candidates:
            vector = []
            try:
                candidate_index = self.candidate_index_in_matrix[candidate.id]
            except KeyError:
                _C.append(zeros(len(self.proposals)))
                continue
            for p in self.proposals:
                proposal_index = self.proposal_index_in_matrix[p.id]
                value = self.all_candidates_and_proposals[candidate_index, proposal_index]
                vector.append(value)
            _C.append(vector)
        return matrix(_C)

    
