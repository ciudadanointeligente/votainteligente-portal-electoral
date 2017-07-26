from __future__ import unicode_literals

from popular_proposal.models import PopularProposal


class KidsProposal(PopularProposal):
    @property
    def is_kids(self):
        return True

    class Meta:
        proxy = True
