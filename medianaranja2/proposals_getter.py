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
