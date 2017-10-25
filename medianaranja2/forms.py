from django import forms
from popular_proposal.models import (PopularProposal
                                     )
from elections.models import Area, QuestionCategory
from django.conf import settings


class SetupForm(forms.Form):
    area = forms.ModelChoiceField(queryset=Area.objects.filter(classification__in=settings.FILTERABLE_AREAS_TYPE))
    categories = forms.ModelMultipleChoiceField(queryset=QuestionCategory.objects.all())


class QuestionsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        super(QuestionsForm, self).__init__(*args, **kwargs)
        for category in self.categories:
            for topic in category.topics.order_by('id'):
                self.fields[topic.slug] = forms.ModelChoiceField(queryset=topic.positions)

    def clean(self):
        cleaned_data = super(QuestionsForm, self).clean()
        cleaned_data['positions'] = []
        for topic in cleaned_data:
            cleaned_data['positions'].append(cleaned_data[topic])

        return cleaned_data

class ProposalsForm(forms.Form):
    proposals = forms.ModelMultipleChoiceField(queryset=PopularProposal.objects.none())

    def __init__(self, *args, **kwargs):
        self.proposals = kwargs.pop('proposals')
        super(ProposalsForm, self).__init__(*args, **kwargs)
        qs = PopularProposal.objects.filter(id__in=[p.id for p in self.proposals])
        self.fields['proposals'].queryset = qs