# coding=utf-8
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     )
from constance import config
from django.core.cache import cache

class ProposalsGetter(object):
    def __init__(self):
        pass

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


    def get_all_proposals(self, area):
        cache_key = 'proposals_for_' + area.id
        if cache.get(cache_key) is not None:
            return cache.get(cache_key)
        elections = self.get_elections(area)
        proposals = PopularProposal.ordered.filter(commitments__candidate__elections__in=elections)
        proposals = list(proposals[:config.MEDIA_NARANJA_MAX_NUM_PR])
        cache.set(cache_key, proposals)
        return proposals[:config.MEDIA_NARANJA_MAX_NUM_PR]