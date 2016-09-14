# coding=utf-8
from django import forms
from backend_candidate.models import add_contact_and_send_mail


class AddContactAndSendMailForm(forms.Form):
    mail = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate')
        super(AddContactAndSendMailForm, self).__init__(*args, **kwargs)

    def send_mail(self):
        add_contact_and_send_mail(self.cleaned_data['mail'], self.candidate)
