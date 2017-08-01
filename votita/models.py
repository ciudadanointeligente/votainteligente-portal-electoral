from __future__ import unicode_literals
from django.db import models
from django.template.loader import get_template
from picklefield.fields import PickledObjectField
from popular_proposal.models import PopularProposal
from multiselectfield import MultiSelectField


PRESIDENTS_FEATURES = (('ingeligente', 'Inteligente'),
                       ('honesto', 'Honesto'),)


class KidsGathering(models.Model):
    name = models.CharField(max_length=255)
    stats_data = PickledObjectField()
    presidents_features = MultiSelectField(choices=PRESIDENTS_FEATURES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)


class KidsProposal(PopularProposal):
    gathering = models.ForeignKey(KidsGathering,
                                  related_name='proposals',
                                  null=True)
    @property
    def is_kids(self):
        return True

    @property
    def card(self):
        return get_template("votita/card.html").render({
            'proposal': self
        })
