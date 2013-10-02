from haystack.forms import SearchForm
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _
from elections.models import Election
from writeit.models import Message

class ElectionForm(SearchForm):
	pass

class ElectionSearchByTagsForm(forms.Form):
	q = forms.CharField(required=False, label=_('Busca tu comuna'))

	def get_search_result(self):
		cleaned_data = self.clean()
		queryed_element = cleaned_data['q']
		return Election.objects.filter(tags__name__in=[queryed_element])


class MessageForm(ModelForm):

	def __init__(self, *args, **kwargs):
		self.writeitinstance = kwargs.pop('writeitinstance')
		super(MessageForm, self).__init__(*args, **kwargs)
		self.instance.writeitinstance = self.writeitinstance
		self.instance.api_instance = self.writeitinstance.api_instance
	class Meta:
		model = Message
		fields = ('author_name', 'author_email', 'subject', 'content','people')
	def save(self, **kwargs):
		message = super(MessageForm, self).save(**kwargs)
		message.push_to_the_api()
		return message

