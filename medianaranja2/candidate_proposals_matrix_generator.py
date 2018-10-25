# coding=utf-8
from numpy import matrix, dot, zeros
from django.core.cache import cache
from elections.models import Candidate
from popular_proposal.models import PopularProposal
from organization_profiles.models import OrganizationTemplate


class CandidateCommitmentsMatrixGenerator(object):
    def __init__(self):
        self.cache_key = 'matrix_proposals_candidates'
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

    def set_cache(self, time=7200):
        m = self._get_matrix_with_all_proposals()
        candidate_index = self.candidate_index_in_matrix
        proposals_index = self.proposal_index_in_matrix
        cache.set(self.cache_key, m, time)
        cache.set('candidate_index_in_matrix', candidate_index, time)
        cache.set('proposal_index_in_matrix', proposals_index, time)
        return m

    def get_matrix_with_all_proposals(self):
        if cache.get(self.cache_key) is not None:
            return cache.get(self.cache_key)
        return self.set_cache()

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


class OrganizationMatrixCreator(object):
    def __init__(self, *args, **kwargs):
        self.cache_key = 'orgs_templates_resultado'
        self.main_matrix, self.proposals_ids, self.organization_ids  = self.get_main_matrix_and_orders()

    def get_selected_proposals_vector(self, proposals):
        r = zeros(len(self.proposals_ids))
        for p in proposals:
            index = self.proposals_ids[p.id]
            r[index] = 1
        return r

    def get_organizations(self, proposals):
        proposals_v = self.get_selected_proposals_vector(proposals)
        m = self.main_matrix
        final_vector = dot(m.T, proposals_v)
        organization_ids = []
        counter = 0
        for i in final_vector:
            if i:
                id_ = self.organization_ids[counter]
                organization_ids.append(id_)
            counter += 1
        return OrganizationTemplate.objects.filter(id__in=organization_ids)

    def get_main_matrix_and_orders(self):
        if cache.get(self.cache_key) is not None:
            return cache.get(self.cache_key)
        return self.set_cache()

    def set_cache(self, time=600):
        r = self._get_main_matrix_and_orders()
        cache.set(self.cache_key, r, time)
        return r

    def _get_main_matrix_and_orders(self):
        main_matrix = zeros((PopularProposal.objects.count(), OrganizationTemplate.objects.count()))
        proposals_ids = {}
        organization_ids = {}
        i = 0
        for p in PopularProposal.objects.all():
            proposals_ids[p.id] = i
            j = 0
            for t in OrganizationTemplate.objects.all():
                organization_ids[j] = t.id
                if((p.proposer==t.organization) or (t.organization in p.likers.all())):
                    main_matrix[i][j] = 1
                j += 1
            i += 1
        return main_matrix, proposals_ids, organization_ids
