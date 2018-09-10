# coding=utf-8
from django import forms
from merepresenta.models import Candidate, QuestionCategory, CandidateQuestionCategory


class QuestionsCategoryForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(queryset=QuestionCategory.objects.all(),
                                                label=u'Olá',
                                                widget=forms.CheckboxSelectMultiple(attrs={'class':"categories-select"}))
