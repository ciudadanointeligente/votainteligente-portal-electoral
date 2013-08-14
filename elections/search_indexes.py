from haystack import indexes
from elections.models import Election

class ElectionIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True)

	def get_model(self):
		return Election