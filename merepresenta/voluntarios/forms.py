# coding=utf-8
from django.forms import ModelForm
from backend_candidate.models import CandidacyContact
from merepresenta.models import VolunteerGetsCandidateEmailLog
from .models import VolunteerProfile


class AddCandidacyContactForm(ModelForm):
    class Meta:
        model = CandidacyContact
        fields = ['mail', ]

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate')
        self.volunteer = kwargs.pop('volunteer')
        super(AddCandidacyContactForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        contact = super(AddCandidacyContactForm, self).save(commit=False)
        contact.candidate = self.candidate
        if commit:
            contact.save()
            VolunteerGetsCandidateEmailLog.objects.create(candidate=self.candidate,
                                                          volunteer=self.volunteer,
                                                          contact=contact)


        return contact


class UpdateAreaForm(ModelForm):
    class Meta:
        model = VolunteerProfile
        fields = ['area', ]
