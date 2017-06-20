from django_filters import FilterSet, ChoiceFilter
from popular_proposal.models import PopularProposal
from popular_proposal.forms.form_texts import TOPIC_CHOICES


class ProposalWithoutAreaFilter(FilterSet):
    clasification = ChoiceFilter(choices=TOPIC_CHOICES)

    def __init__(self, area=None, data=None, queryset=None, prefix=None, strict=None):
        self.area = area
        if queryset is None:
            queryset = PopularProposal.objects.all()
        if self.area is not None:
            queryset = queryset.filter(area=self.area)
        super(ProposalWithoutAreaFilter, self).__init__(data=data,
                                                        queryset=queryset,
                                                        prefix=prefix,
                                                        strict=strict)

    class Meta:
        model = PopularProposal
        fields = ['clasification', ]
