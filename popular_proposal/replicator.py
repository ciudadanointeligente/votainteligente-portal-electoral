from elections.models import Area
from popular_proposal.models import PopularProposal


class Replicator(object):
    def __init__(self, proposal):
        self.proposal = proposal

    def replicate(self, exclude=[]):
        exclude.append(self.proposal.area.id)
        for area in Area.objects.all().exclude(id__in=exclude):
            PopularProposal.objects.create(proposer=self.proposal.proposer,
                                           area=area,
                                           data=self.proposal.data,
                                           clasification=self.proposal.clasification,
                                           title=self.proposal.title,
                                           for_all_areas=True)
        self.proposal.for_all_areas = True
        self.proposal.save()
