# coding=utf-8
from django import forms
from merepresenta.models import Candidate, QuestionCategory, CandidateQuestionCategory
from elections.models import Area


class QuestionsCategoryForm(forms.Form):
    area = forms.ModelChoiceField(queryset=Area.objects.all(),
                                  label=u'Qual o seu estado?', required=False, empty_label=u'Todos os estados')
    categories = forms.ModelMultipleChoiceField(queryset=QuestionCategory.objects.all(),
                                                label=u'Olá',
                                                widget=forms.CheckboxSelectMultiple(attrs={'class':"categories-select"}))
