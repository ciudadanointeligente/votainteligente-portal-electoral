# coding=utf-8
from django import forms
from popular_proposal.models import ProposalTemporaryData

WHEN_CHOICES = [
    ('6_months', u'6 Meses'),
    ('1_year', u'1 año'),
    ('2_year', u'2 años'),
    ('3_year', u'3 años'),
    ('4_year', u'4 años'),
]
class ProposalForm(forms.Form):
    your_name = forms.CharField(label=u'Tu nombre o el de tu organización')
    problem = forms.CharField()
    solution = forms.CharField()
    when = forms.ChoiceField(choices=WHEN_CHOICES)
    allies =  forms.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.area = kwargs.pop('area')
        super(ProposalForm, self).__init__(*args, **kwargs)

    def save(self):
        return ProposalTemporaryData.objects.create(user=self.user,
                                                    area=self.area,
                                                    data=self.cleaned_data)

class CommentsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.temporary_data = kwargs.pop('temporary_area')
        super(CommentsForm, self).__init__(*args, **kwargs)
        for field in self.temporary_data.comments.keys():
            self.fields[field] = forms.CharField()
