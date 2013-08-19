from haystack.forms import SearchForm
from django import forms
from django.utils.translation import ugettext as _
from elections.models import Election

class ElectionForm(SearchForm):
	pass

class ElectionSearchByTagsForm(forms.Form):
	q = forms.CharField(label=_('Busca tu comuna'))

	def get_search_result(self):
		cleaned_data = self.clean()
		queryed_element = cleaned_data['q']
		return Election.objects.filter(tags__name__in=[queryed_element])