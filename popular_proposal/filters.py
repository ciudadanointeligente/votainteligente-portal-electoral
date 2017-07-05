# coding=utf-8
from django_filters import (FilterSet,
                            ChoiceFilter,
                            ModelChoiceFilter,
                            )
from popular_proposal.models import PopularProposal
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from elections.models import Area
from django.conf import settings
from django.forms import CharField, Form
from haystack.query import SearchQuerySet


def filterable_areas(request):
    if settings.FILTERABLE_AREAS_TYPE:
        return Area.public.filter(classification__in=settings.FILTERABLE_AREAS_TYPE)
    return Area.public.all()


class TextSearchForm(Form):
    text = CharField(label=u'Qué buscas?', required=False)

    def full_clean(self):
        super(TextSearchForm, self).full_clean()
        cleaned_data = {}
        for k in self.cleaned_data:
            v = self.cleaned_data.get(k, '')

            if (isinstance(v, unicode) or isinstance(v, str)) and not v.strip():
                cleaned_data[k] = None
        self.cleaned_data.update(cleaned_data)


class ProposalWithoutAreaFilter(FilterSet):
    clasification = ChoiceFilter(choices=TOPIC_CHOICES, label=u"Clasificación")

    def __init__(self,
                 data=None,
                 queryset=None,
                 prefix=None,
                 strict=None,
                 **kwargs):
        self.area = kwargs.pop('area', None)
        if self.area is None and data is not None:
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
        is_filled_search = False
        for k in self.data:
            i = self.data[k]
            is_filled_search = True
            self._form.fields[k].initial = i
        self._form.is_filled_search = is_filled_search
        return self._form

    @property
    def qs(self):

        super(ProposalWithoutAreaFilter, self).qs
        if not self.form.is_valid():
            return self._qs
        text = self.form.cleaned_data.get('text', '')

        if text:
            pks = []
            text_search = SearchQuerySet().models(self._meta.model).auto_query(text)
            for r in text_search:
                pks.append(r.pk)
            return self._qs.filter(id__in=pks)
        return self._qs

    class Meta:
        model = PopularProposal
        fields = ['clasification', ]
        form = TextSearchForm


def possible_areas(request):
    as_ = Area.public.all()
    return as_


class ProposalWithAreaFilter(ProposalWithoutAreaFilter):
    area = ModelChoiceFilter(queryset=possible_areas, label="Comuna donde fue generada")


class ProposalGeneratedAtFilter(ProposalWithoutAreaFilter):
    generated_at = ModelChoiceFilter(queryset=filterable_areas)
