# coding=utf-8
from django_filters import (FilterSet,
                            ChoiceFilter,
                            ModelChoiceFilter,
                            ModelChoiceFilter)
from popular_proposal.models import PopularProposal
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from elections.models import Area
from django.conf import settings


def filterable_areas(request):
    return Area.public.filter(classification__in=settings.FILTERABLE_AREAS_TYPE)

class ProposalWithoutAreaFilter(FilterSet):
    clasification = ChoiceFilter(choices=TOPIC_CHOICES, label=u"Clasificación")

    def __init__(self,
                 data=None,
                 queryset=None,
                 prefix=None,
                 strict=None,
                 **kwargs):
        self.area = kwargs.pop('area', None)
        if self.area is None:
            self.area = data.get('area', None)
            if self.area:
                self.area = Area.objects.get(id=self.area)
        if queryset is None:
            queryset = PopularProposal.objects.all()
        if self.area is not None:
            queryset = queryset.filter(area=self.area)
        super(ProposalWithoutAreaFilter, self).__init__(data=data,
                                                        queryset=queryset,
                                                        prefix=prefix,
                                                        strict=strict)

    @property
    def form(self):
        super(ProposalWithoutAreaFilter, self).form
        
        for k in self.data:
            self._form.fields[k].initial = self.data[k]
        return self._form

    class Meta:
        model = PopularProposal
        fields = ['clasification', ]


def possible_areas(request):
    as_ = Area.public.all()
    return as_

class ProposalWithAreaFilter(ProposalWithoutAreaFilter):
    area = ModelChoiceFilter(queryset=possible_areas)


class ProposalGeneratedAtFilter(ProposalWithoutAreaFilter):
    generated_at = ModelChoiceFilter(queryset=filterable_areas)