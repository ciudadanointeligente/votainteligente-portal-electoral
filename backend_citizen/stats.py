from popular_proposal.models import (PopularProposal)


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
