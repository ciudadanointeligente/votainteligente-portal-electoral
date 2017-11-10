# coding=utf-8
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     )
from constance import config
from django.core.cache import cache
from medianaranja2.models import ReadingGroup


class ProposalsGetterBase(object):
    def proposals(self, election):
        commitments = Commitment.objects.filter(commited=True, candidate__elections=election)
        return list(PopularProposal.objects.filter(commitments__in=commitments).distinct())

    def get_elections(self, area):
        has_parent = True
        elections = []
        while has_parent:
            if area.elections.all():
                elections += list(area.elections.all())
            if not area.parent:
                has_parent = False
            else:
                area = area.parent
        return elections

    def get_proposals_from_election(self, elections):
        raise NotImplementedError

    def get_all_proposals(self, area):
        cache_key =  self.cache_key + area.id
        if cache.get(cache_key) is not None:
            return cache.get(cache_key)
        elections = self.get_elections(area)
        proposals = self.get_proposals_from_election(elections)
        cache.set(cache_key, proposals)
        return proposals

class ProposalsGetter(ProposalsGetterBase):
    cache_key = 'proposals_for_'
    
    def get_proposals_from_election(self, elections):
        return PopularProposal.ordered.filter(commitments__candidate__elections__in=elections).order_by('-num_likers')


class ProposalsGetterByReadingGroup(ProposalsGetterBase):
    cache_key = 'proposals_by_reading_group_for_'

    def get_proposals_from_election(self, elections):
        ids = []
        reading_groups_proposals = {}
        for reading_group in ReadingGroup.objects.all():
            reading_groups_proposals[reading_group.id] = reading_group.get_proposals(elections=elections)
        index = 0
        for _id in reading_groups_proposals:
            proposal_id = reading_groups_proposals[_id][index].id
            if proposal_id not in ids:
                ids.append(proposal_id)
                if len(ids) == config.MEDIA_NARANJA_MAX_NUM_PR:
                    return PopularProposal.objects.filter(id__in=ids)