from django_filters import FilterSet, ChoiceFilter, ModelChoiceFilter
from popular_proposal.models import PopularProposal
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from elections.models import Area


class ProposalWithoutAreaFilter(FilterSet):
    clasification = ChoiceFilter(choices=TOPIC_CHOICES)

    def __init__(self,
                 data=None,
                 queryset=None,
                 prefix=None,
                 strict=None,
                 **kwargs):
        self.area = None
        if kwargs:
            self.area = kwargs.pop('area', None)
        if self.area is None:
            self.area = data.pop('area', None)
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


def possible_areas(request):
    as_ = Area.public.all()
    return as_

class ProposalWithAreaFilter(ProposalWithoutAreaFilter):
    area = ModelChoiceFilter(queryset=possible_areas)