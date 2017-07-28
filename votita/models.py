from __future__ import unicode_literals
from django.template.loader import get_template

from popular_proposal.models import PopularProposal


class KidsProposal(PopularProposal):
    @property
    def is_kids(self):
        return True

    @property
    def card(self):
        return get_template("votita/card.html").render({
            'proposal': self
        })
