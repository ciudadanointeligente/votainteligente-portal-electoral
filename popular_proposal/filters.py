# coding=utf-8
from copy import copy

from django_filters import (FilterSet,
                            ChoiceFilter,
                            ModelChoiceFilter,
                            )
from popular_proposal.models import PopularProposal
from elections.models import Area
from django.conf import settings
from constance import config
from django.forms import CharField, Form, ChoiceField, HiddenInput
from haystack.query import SearchQuerySet
from django.utils.translation import ugettext_lazy as _


def filterable_areas(request):
    areas = Area.public.all().exclude(proposals_generated_here__isnull=True)
    if settings.FILTERABLE_AREAS_TYPE:
        return areas.filter(classification__in=settings.FILTERABLE_AREAS_TYPE)
    return areas


class TextSearchForm(Form):
    text = CharField(label=_(u'Qué buscas?'), required=False)
    order_by = ChoiceField(required=False,
                           label=_(u"Ordenar por"),
                           choices=[('', _(u'Por apoyos')),
                                    ('-created', _(u'Últimas primero')),
                                    ('-proposer__profile__is_organization', _(u'De organizaciones primero')),
                                    ('-is_local_meeting', _(u'Encuentros locales primero')),
                                    ])

    def full_clean(self):
        super(TextSearchForm, self).full_clean()
        cleaned_data = {}
        for k in self.cleaned_data:
            v = self.cleaned_data.get(k, '')

            if (isinstance(v, unicode) or isinstance(v, str)) and not v.strip():
                cleaned_data[k] = None
        self.cleaned_data.update(cleaned_data)


class ProposalWithoutAreaFilter(FilterSet):
    clasification = ChoiceFilter(choices=[],
                                 empty_label=_(u"Selecciona"),
                                 widget=HiddenInput(),
                                 label=_(u"Clasificación"))

    def __init__(self,
                 data=None,
                 queryset=None,
                 prefix=None,
                 strict=None,
                 **kwargs):
        self.area = kwargs.pop('area', None)
        d = copy(data)
        if self.area is None and data is not None:
            self.area = data.get('area', None)
            if self.area:
                try:
                    self.area = Area.objects.get(slug=self.area)
                except Area.DoesNotExist as e:
                    self.area = None
        if queryset is None:
            queryset = PopularProposal.ordered.all()
        if self.area is not None:
            queryset = queryset.filter(area=self.area)
            if d and self.area:
                print("<----------------", self.area)
                d['area'] = self.area.id
        super(ProposalWithoutAreaFilter, self).__init__(data=d,
                                                        queryset=queryset,
                                                        prefix=prefix,
                                                        strict=strict)
        from popular_proposal.forms.form_texts import TOPIC_CHOICES
        self.form.fields['clasification'].choices = TOPIC_CHOICES

    @property
    def form(self):
        super(ProposalWithoutAreaFilter, self).form
        is_filled_search = False
        for k in self.data:
            i = self.data[k]
            is_filled_search = True
            if k in self._form.fields:
                self._form.fields[k].initial = i
        self._form.is_filled_search = is_filled_search
        return self._form

    @property
    def qs(self):

        super(ProposalWithoutAreaFilter, self).qs
        if not self.form.is_valid():
            return self._qs
        order_by = self.form.cleaned_data.get('order_by', None)
        if order_by:
            self._qs = self._qs.order_by(order_by)
        else:
            self._qs = self._qs.by_likers()
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
    area = ModelChoiceFilter(queryset=possible_areas, label=_(u"Comuna donde fue generada"))


class ProposalGeneratedAtFilter(ProposalWithoutAreaFilter):
    generated_at = ModelChoiceFilter(queryset=filterable_areas,
                                     empty_label=_(u"Selecciona"),
                                     label=_(u"Comuna donde fue generada"))
