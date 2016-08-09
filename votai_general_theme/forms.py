from django import forms


class PersonalDataForm(forms.Form):
	age = forms.IntegerField(label='Edad')
	party = forms.CharField(label='Partido')
