# coding=utf-8
from haystack import indexes
from popular_proposal.models import PopularProposal


class ProposalIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)

	def get_model(self):
		return PopularProposal

	def index_queryset(self, using=None):
		return PopularProposal.objects.all()