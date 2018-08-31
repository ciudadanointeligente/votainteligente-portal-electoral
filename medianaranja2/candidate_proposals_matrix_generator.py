# coding=utf-8
from numpy import matrix
from django.core.cache import cache
from elections.models import Candidate
from popular_proposal.models import PopularProposal


class CandidateCommitmentsMatrixGenerator(object):
    def __init__(self):
        self.candidate_index_in_matrix = {}
        self.proposal_index_in_matrix = {}

    def _set_candidate_index_in_matrix(self, candidate, index):
        self.candidate_index_in_matrix[candidate.id] = index

    def _get_candidate_index_in_matrix(self):
        cache_key = 'candidate_index_in_matrix'
        if cache.get(cache_key) is not None:
            return cache.get(cache_key)
        else:
            cache.set('candidate_index_in_matrix', self.candidate_index_in_matrix)
            return self.candidate_index_in_matrix

    def _get_proposal_index_in_matrix(self):
        cache_key = 'proposal_index_in_matrix'
        if cache.get(cache_key) is not None:
            return cache.get(cache_key)
        else:
            cache.set('proposal_index_in_matrix', self.proposal_index_in_matrix)
            return self.proposal_index_in_matrix

    def _set_proposal_index_in_matrix(self, proposal, index):
        self.proposal_index_in_matrix[proposal.id] = index

    def get_matrix_with_all_proposals(self):
        cache_key = 'matrix_proposals_candidates'
        if cache.get(cache_key) is not None:
            m = cache.get(cache_key)
        else:
            m = self._get_matrix_with_all_proposals()
            cache.set(cache_key, m)
            cache.set('candidate_index_in_matrix', self.candidate_index_in_matrix)
            cache.set('proposal_index_in_matrix', self.proposal_index_in_matrix)
        return m

    def _get_matrix_with_all_proposals(self):
        _C = []
        candidate_index = 0
        all_proposals = PopularProposal.objects.all()
        for candidate in Candidate.objects.filter(commitments__isnull=False):
            vector = []
            self._set_candidate_index_in_matrix(candidate, candidate_index)
            candidate_index += 1
            proposal_index = 0
            for p in all_proposals:
                self._set_proposal_index_in_matrix(p, proposal_index)
                proposal_index += 1
                if candidate.commitments.filter(proposal=p, commited=True).exists():
                    vector.append(1)
                else:
                    vector.append(0)
            _C.append(vector)
        return matrix(_C)