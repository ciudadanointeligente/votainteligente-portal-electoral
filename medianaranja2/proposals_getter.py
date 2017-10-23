# coding=utf-8
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     )

class ProposalsGetter(object):
    def __init__(self):
        pass

    def proposals(self, election):
        commitments = Commitment.objects.filter(commited=True, candidate__elections=election)
        return list(PopularProposal.objects.filter(commitments__in=commitments).distinct())

    def get_all_proposals(self, area):
        proposals = []
        has_parent = True
        while has_parent:
            if area.elections.all():
                for election in area.elections.all():
                    proposals += self.proposals(election)
            if not area.parent:
                has_parent = False
            else:
                area = area.parent
        return proposals