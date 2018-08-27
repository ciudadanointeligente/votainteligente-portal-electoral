# coding=utf-8
from django import forms
from backend_candidate.models import CandidacyContact
from merepresenta.models import VolunteerGetsCandidateEmailLog
from .models import VolunteerProfile
from votai_utils.send_mails import send_mail


class VolunteerGetsCandidateEmailLogMixin(object):
    def _save_log(self, contact=None):
        c = contact or self.contact or None
        VolunteerGetsCandidateEmailLog.objects.create(candidate=self.candidate,
                                                      volunteer=self.volunteer,
                                                      contact=c)


class AddCandidacyContactForm(forms.ModelForm, VolunteerGetsCandidateEmailLogMixin):
    class Meta:
        model = CandidacyContact
        fields = ['mail', ]

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate')
        self.volunteer = kwargs.pop('volunteer')
        super(AddCandidacyContactForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.contact = super(AddCandidacyContactForm, self).save(commit=False)
        self.contact.candidate = self.candidate
        if commit:
            self.contact.save()
            self._save_log()
        return self.contact


class UpdateAreaForm(forms.ModelForm):
    class Meta:
        model = VolunteerProfile
        fields = ['area', ]
        labels = {'area': u'Escolha o Estado:'}


class VoluntarioCandidateHuntForm(forms.Form, VolunteerGetsCandidateEmailLogMixin):
    facebook = forms.BooleanField(required=False, label=u"Sim, encontrei! :)")
    tse_email = forms.BooleanField(required=False, label=u"Sim, enviar um e-mail")
    other_email = forms.EmailField(required=False, label=u"Cole aqui o email que você encontrou que a gente manda a mensagem!")

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate')
        self.volunteer = kwargs.pop('volunteer')
        super(VoluntarioCandidateHuntForm, self).__init__(*args, **kwargs)

    def save(self):
        mail = self.cleaned_data['other_email']
        context = {
            'candidate': self.candidate.name
        }
        if self.cleaned_data['tse_email']:
            CandidacyContact.objects.create(mail=self.cleaned_data['tse_email'], candidate=self.candidate)
            send_mail(context, 'contato_novo_com_candidato', to=[self.candidate.original_email],)

        if self.cleaned_data['other_email']:
            CandidacyContact.objects.create(mail=self.cleaned_data['other_email'], candidate=self.candidate)
            send_mail(context, 'contato_novo_com_candidato', to=[self.cleaned_data['other_email']],)

        if self.cleaned_data['facebook']:
            CandidacyContact.objects.create(candidate=self.candidate)

