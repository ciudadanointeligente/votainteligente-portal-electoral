# coding=utf-8
from django import forms
from django.forms import formset_factory
from django.forms import BaseFormSet
from popular_proposal.models import Commitment


class SimpleCommitmentForm(forms.Form):
    commited = forms.NullBooleanField(label=u"Me comprometo con esta propuesta.",
                                      widget=forms.CheckboxInput,
                                      required=False)
    detail = forms.CharField(label=u"Los términos a los que me comprometo con esta propuesta son",
                             widget=forms.Textarea(attrs={'rows': 5, 'cols': 40,}),
                             required=False)

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate')
        self.proposal = kwargs.pop('proposal')
        self.summary = kwargs.pop('summary', None)
        return super(SimpleCommitmentForm, self).__init__(*args, **kwargs)

    def save(self):
        initial_commitment_kwargs = {"proposal": self.proposal, "candidate": self.candidate}
        if self.cleaned_data['commited'] and not Commitment.objects.filter(**initial_commitment_kwargs):
            initial_commitment_kwargs.update(**self.cleaned_data)
            return Commitment.objects.create(**initial_commitment_kwargs)

def get_multi_commitment_forms(candidate, proposals, summaries):
    class BaseCommitmentFormSet(BaseFormSet):
        def get_form_kwargs(self, index):
            kwargs = super(BaseCommitmentFormSet, self).get_form_kwargs(index)
            kwargs['proposal'] = proposals[index]
            kwargs['summary'] = summaries[index]
            kwargs['candidate'] = candidate
            return kwargs

        def save(self):
            commitments = []
            for f in self.forms:
                c = f.save()
                if c is not None:
                    commitments.append(c)
            return commitments

    num_forms = len(proposals)
    return formset_factory(SimpleCommitmentForm,
                           formset=BaseCommitmentFormSet,
                           max_num=num_forms,
                           min_num=num_forms, )