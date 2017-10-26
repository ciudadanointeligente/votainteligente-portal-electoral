from django import forms
from popular_proposal.models import (PopularProposal
                                     )
from elections.models import Area, QuestionCategory
from django.conf import settings
from formtools.wizard.views import SessionWizardView
from medianaranja2.proposals_getter import ProposalsGetter
from django.shortcuts import render
from medianaranja2.calculator import Calculator


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
        r = {"positions": []}
        for topic in cleaned_data:
            r['positions'].append(cleaned_data[topic])

        return r

class ProposalsForm(forms.Form):
    proposals = forms.ModelMultipleChoiceField(queryset=PopularProposal.objects.none())

    def __init__(self, *args, **kwargs):
        self.proposals = kwargs.pop('proposals')
        super(ProposalsForm, self).__init__(*args, **kwargs)
        qs = PopularProposal.objects.filter(id__in=[p.id for p in self.proposals])
        self.fields['proposals'].queryset = qs


FORMS = [SetupForm, QuestionsForm, ProposalsForm]

class MediaNaranjaWizardForm(SessionWizardView):
    form_list = FORMS

    def done(self, form_list, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        results = []
        has_parent = True
        area = cleaned_data['area']
        while has_parent:
            if area.elections.all():
                for election in area.elections.all():
                    calculator = Calculator(election, cleaned_data['positions'], cleaned_data['proposals'])
                    results.append(calculator.get_result())
            if not area.parent:
                has_parent = False
            else:
                area = area.parent
        return render(self.request, 'medianaranja2/resultado.html', {
            'results': results,
        })



    def get_form_kwargs(self, step):
        step = int(step)
        if step == 1:
            cleaned_data = self.get_cleaned_data_for_step(str(0))
            return {'categories': list(cleaned_data['categories'])}
        if step == 2:
            cleaned_data = self.get_cleaned_data_for_step(str(0))
            getter = ProposalsGetter()
            proposals = getter.get_all_proposals(cleaned_data['area'])
            return {'proposals': proposals}

        return {}