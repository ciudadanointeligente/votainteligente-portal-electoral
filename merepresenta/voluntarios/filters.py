# coding=utf-8
from django_filters import (
                            ModelChoiceFilter,
                            )
from django_filters.filterset import FilterSet
from merepresenta.models import Candidate
from elections.models import Area




class CandidateFilter(FilterSet):
    elections__area = ModelChoiceFilter(queryset=Area.objects.filter(classification='state'))


    class Meta:
        model = Candidate
        fields = ['elections__area']