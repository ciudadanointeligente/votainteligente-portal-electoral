# coding=utf-8
from django.db import models
from elections.models import Candidate
from popular_proposal.models import PopularProposal
from picklefield.fields import PickledObjectField
from django.contrib.contenttypes.models import ContentType
import uuid
from django.core.urlresolvers import reverse


class ReadingGroup(models.Model):
    name = models.CharField(max_length=512)
    candidates = models.ManyToManyField(Candidate, related_name='groups')

    def get_proposals(self, elections=None):
        qs = PopularProposal.ordered.all()
        candidates = self.candidates
        if elections is not None:
            candidates = candidates.filter(elections__in=elections)
        qs = qs.filter(commitments__candidate__in=candidates.all())
        qs = qs.order_by('-num_likers')
        return qs


class SharedResult(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4)
    data = PickledObjectField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('medianaranja2:share', kwargs={'identifier': self.identifier})
