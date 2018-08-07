# coding=utf-8
from django import forms
from backend_candidate.models import Candidacy
from merepresenta.models import Candidate, QuestionCategory, CandidateQuestionCategory
from backend_candidate.forms import MediaNaranjaSingleCandidateMixin, MediaNaranjaSingleCategoryMixin


class CPFAndDdnFormBase(forms.Form):
    cpf = forms.CharField(required=True)
    nascimento = forms.DateField(required=True, input_formats=['%d/%m/%Y','%d/%m/%y', '%d-%m-%Y', '%d-%m-%y',])

class CPFAndDdnForm(CPFAndDdnFormBase):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CPFAndDdnForm, self).__init__(*args, **kwargs)

    def clean(self):
        cpf = self.cleaned_data['cpf']
        ddn = self.cleaned_data.get('nascimento', None)
        if ddn is None:
            raise forms.ValidationError(u'Não encontramos o candidato')
        try:
            self.candidate = Candidate.objects.get(cpf=cpf, data_de_nascimento=ddn)
        except Candidate.DoesNotExist:
            raise forms.ValidationError(u'Não encontramos o candidato')
        return self.cleaned_data

    def save(self):
        return Candidacy.objects.create(user=self.user, candidate=self.candidate)


class CPFAndDdnForm2(CPFAndDdnFormBase):
    def clean(self):
        cpf = self.cleaned_data['cpf']
        ddn = self.cleaned_data.get('nascimento', None)
        if ddn is None:
            raise forms.ValidationError(u'Não encontramos o candidato')
        try:
            self.candidate = Candidate.objects.get(cpf=cpf, data_de_nascimento=ddn)
        except Candidate.DoesNotExist:
            raise forms.ValidationError(u'Não encontramos o candidato')
        return self.cleaned_data

    def get_candidate(self):
        return self.candidate


class MeRepresentaCandidateAnsweringForm(MediaNaranjaSingleCandidateMixin, forms.Form, MediaNaranjaSingleCategoryMixin):
    def __init__(self, *args, **kwargs):
        super(MeRepresentaCandidateAnsweringForm, self).__init__(*args, **kwargs)
        self.set_fields_for(self.category)

    def save(self):
        self.save_answer_for(self.category)




def get_form_class_from_category(category, candidate):
    class OnDemandMeRepresentaCandidateAnsweringForm(MeRepresentaCandidateAnsweringForm):
        def __init__(self, *args, **kwargs):
            self.category = category
            kwargs['candidate'] = candidate
            super(OnDemandMeRepresentaCandidateAnsweringForm, self).__init__(*args, **kwargs)

    return OnDemandMeRepresentaCandidateAnsweringForm

class CategoryCandidateForm(MediaNaranjaSingleCandidateMixin, forms.Form):
    categories = forms.ModelMultipleChoiceField(queryset=QuestionCategory.objects.all())

    def save(self):
        for category in self.cleaned_data['categories']:
            if not isinstance(self.candidate, Candidate):
                self.candidate = Candidate.objects.get(candidate_ptr_id=self.candidate.id)
            CandidateQuestionCategory.objects.create(category=category, candidate=self.candidate)

def get_last_form(candidate):
    class OnDemandMeRepresentaCandidateCategoryForm(CategoryCandidateForm):
        def __init__(self, *args, **kwargs):
            kwargs['candidate'] = candidate
            super(OnDemandMeRepresentaCandidateCategoryForm, self).__init__(*args, **kwargs)

    return OnDemandMeRepresentaCandidateCategoryForm

def get_form_classes_for_questions_for(candidate):
    result = []
    categories = QuestionCategory.objects.all()
    for category in categories:
        form_class = get_form_class_from_category(category, candidate)
        result.append(form_class)

    result.append(get_last_form(candidate))
    return result


