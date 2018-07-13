# coding=utf-8
from django.forms import ModelForm
from backend_candidate.models import CandidacyContact


class AddCandidacyContactForm(ModelForm):
    class Meta:
        model = CandidacyContact
        fields = ['mail', ]

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate')
        super(AddCandidacyContactForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        contact = super(AddCandidacyContactForm, self).save(commit=False)
        contact.candidate = self.candidate
        if commit:
            contact.save()
        return contact