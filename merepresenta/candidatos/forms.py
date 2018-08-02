# coding=utf-8
from django import forms
from backend_candidate.models import Candidacy
from merepresenta.models import Candidate


class CPFAndDdnForm(forms.Form):
    cpf = forms.CharField(required=True)
    nascimento = forms.DateField(required=True, input_formats=['%d/%m/%Y','%d/%m/%y', '%d-%m-%Y', '%d-%m-%y',])

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