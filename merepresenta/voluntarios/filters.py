# coding=utf-8
from django_filters import (
                            ModelChoiceFilter,
                            )
from django_filters.filterset import FilterSet
from merepresenta.models import Candidate
from elections.models import Area
from django.conf import settings



def get_areas_for_filtering():
    if settings.FILTERABLE_AREAS_TYPE:
        state_classification = settings.FILTERABLE_AREAS_TYPE[0]
    else:
        state_classification = 'state'

    return Area.objects.filter(classification=state_classification)

class CandidateFilter(FilterSet):
    elections__area = ModelChoiceFilter(queryset=Area.objects.none())


    def __init__(self, *args, **kwargs):
        super(CandidateFilter, self).__init__(*args, **kwargs)
        self.form.fields['elections__area'].queryset = get_areas_for_filtering()


    class Meta:
        model = Candidate
        fields = ['elections__area']