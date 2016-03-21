# coding=utf-8
from django import forms

WHEN_CHOICES = [
    ('6_months', u'6 Meses'),
    ('1_year', u'1 año'),
    ('2_year', u'2 años'),
    ('3_year', u'3 años'),
    ('4_year', u'4 años'),
]
class ProposalForm(forms.Form):
    your_name = forms.CharField(label=u'Tu nombre o el de tu organización')
    email = forms.EmailField()
    problem = forms.CharField()
    solution = forms.CharField()
    when = forms.ChoiceField(choices=WHEN_CHOICES)
    allies =  forms.CharField()
