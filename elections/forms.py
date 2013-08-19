from haystack.forms import SearchForm
from django import forms
from django.utils.translation import ugettext as _

class ElectionForm(SearchForm):
	pass

class ElectionSearchByTagsForm(forms.Form):
	q = forms.CharField(required=False, label=_('Busca tu comuna'))