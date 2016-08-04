from django_filters import FilterSet, ChoiceFilter
from popular_proposal.models import PopularProposal
from popular_proposal.forms.form_texts import TOPIC_CHOICES


class ProposalAreaFilter(FilterSet):
	clasification = ChoiceFilter(choices=TOPIC_CHOICES)

	def __init__(self, area=None, data=None, queryset=None, prefix=None, strict=None):
		self.area = area
		queryset = PopularProposal.objects.filter(area=self.area)

		super(ProposalAreaFilter, self).__init__(data, queryset, prefix, strict)

	class Meta:
		model = PopularProposal
		fields = ['clasification', ]
