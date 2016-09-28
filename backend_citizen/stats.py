from popular_proposal.models import (PopularProposal, Commitment)
from elections.models import Area


class StatsPerAreaPerUser(object):
    def __init__(self, area, user):
        self.area = area
        self.user = user

        self.local_proposals = PopularProposal.objects.filter(proposer=self.user,
                                                              area=self.area,
                                                              for_all_areas=False)
        self.for_all_areas_proposals = PopularProposal.objects.filter(proposer=self.user,
                                                                      area=self.area,
                                                                      for_all_areas=True)
        self.all_proposals = PopularProposal.objects.filter(proposer=self.user,
                                                            area=self.area)


class StatsPerProposal(object):
    def __init__(self, proposal):
        self.proposal = proposal
        self.all_pronouncings = Commitment.objects.filter(proposal=self.proposal)
        self.commitment_qs = self.all_pronouncings
        super(StatsPerProposal, self).__init__()

    def pronouncing(self):
        return self.commitment_qs

    def __getattribute__(self, name):
        if name.startswith('pronouncing__'):
            field_and_value = name.split('__')
            filter_args = {'candidate__elections__position': field_and_value[1]}
            self.commitment_qs = self.all_pronouncings.filter(**filter_args)
            return self.pronouncing
        return super(StatsPerProposal, self).__getattribute__(name)


class PerUserTotalStats(object):
    def __init__(self, user):
        self.user = user
        self.all_pronouncings = Commitment.objects.filter(proposal__proposer=self.user).exclude(commited=False)
        self.commitment_qs = self.all_pronouncings
        super(PerUserTotalStats, self).__init__()

    def areas_present(self):
        return Area.objects.filter(proposals__proposer=self.user).distinct()

    def areas_with_commitments(self):
        return self.areas_present().filter(proposals__commitments__isnull=False).distinct()

    def pronouncing(self):
        return self.commitment_qs

    def __getattribute__(self, name):
        if name.startswith('pronouncing__'):
            field_and_value = name.split('__')
            filter_args = {'candidate__elections__position': field_and_value[1]}
            self.commitment_qs = self.all_pronouncings.filter(**filter_args)
            return self.pronouncing
        return super(PerUserTotalStats, self).__getattribute__(name)