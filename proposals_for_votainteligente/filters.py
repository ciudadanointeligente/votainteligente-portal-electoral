# coding=utf-8
from django_filters import (FilterSet,
                            ChoiceFilter,
                            ModelChoiceFilter,
                            )
from popular_proposal.models import PopularProposal
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from elections.models import Area
from django.conf import settings
from constance import config
from django.forms import CharField, Form, ChoiceField, HiddenInput
from haystack.query import SearchQuerySet
from popular_proposal.filters import ProposalFilterBase




class ProposalFilterBase(ProposalFilterBase):


    def filter_original_queryset(self,
                 data=None,
                 queryset=None,
                 prefix=None,
                 strict=None,
                 **kwargs):
        self.area = kwargs.pop('area', None)
        if self.area is None and data is not None:
            self.area = data.get('area', None)
            if self.area:
                try:
                    self.area = Area.objects.get(id=self.area)
                except Area.DoesNotExist as e:
                    self.area = None
        if self.area is not None:
            queryset = queryset.filter(area=self.area)
        return queryset


def possible_areas(request):
    as_ = Area.public.all()
    return as_


class ProposalWithAreaFilter(ProposalFilterBase):
    area = ModelChoiceFilter(queryset=possible_areas, label="Comuna donde fue generada")



def filterable_areas(request):
    areas = Area.public.all().exclude(popularproposals_generated_here__isnull=True)
    if settings.FILTERABLE_AREAS_TYPE:
        return areas.filter(classification__in=settings.FILTERABLE_AREAS_TYPE)
    return areas
 
 
class ProposalGeneratedAtFilter(ProposalFilterBase):
    generated_at = ModelChoiceFilter(queryset=filterable_areas,
                                     empty_label=u"Selecciona",
                                     label="Comuna donde fue generada")
