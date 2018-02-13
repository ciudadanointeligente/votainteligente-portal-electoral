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



class TextSearchForm(Form):
    text = CharField(label=u'Qué buscas?', required=False)
    order_by = ChoiceField(required=False,
                           label=u"Ordenar por",
                           choices=[('', u'Por apoyos'),
                                    ('-created', u'Últimas primero'),
                                    ('-proposer__profile__is_organization', u'De organizaciones primero'),
                                    ('-is_local_meeting', u'Encuentros locales primero'),
                                    ])

    def full_clean(self):
        super(TextSearchForm, self).full_clean()
        cleaned_data = {}
        for k in self.cleaned_data:
            v = self.cleaned_data.get(k, '')

            if (isinstance(v, unicode) or isinstance(v, str)) and not v.strip():
                cleaned_data[k] = None
        self.cleaned_data.update(cleaned_data)


class ProposalFilterBase(FilterSet):
    clasification = ChoiceFilter(choices=TOPIC_CHOICES,
                                 empty_label=u"Selecciona",
                                 widget=HiddenInput(),
                                 label=u"Clasificación")

    def __init__(self,
                 data=None,
                 queryset=None,
                 prefix=None,
                 strict=None,
                 **kwargs):
        if queryset is None:
            queryset = PopularProposal.ordered.all()

        queryset = self.filter_original_queryset(data, queryset, prefix, strict, **kwargs)
        super(ProposalFilterBase, self).__init__(data=data,
                                                        queryset=queryset,
                                                        prefix=prefix,
                                                        strict=strict)

    def filter_original_queryset(self,
                 data=None,
                 queryset=None,
                 prefix=None,
                 strict=None,
                 **kwargs):
        return queryset

    @property
    def form(self):
        super(ProposalFilterBase, self).form
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

        super(ProposalFilterBase, self).qs
        self._qs = self._qs.exclude(area__id=config.HIDDEN_AREAS)
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
