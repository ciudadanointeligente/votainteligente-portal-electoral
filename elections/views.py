# Create your views here.
from django.views.generic.edit import FormView
from elections.forms import ElectionSearchByTagsForm

class ElectionsSearchByTagView(FormView):
	form_class = ElectionSearchByTagsForm
	template_name = 'search/tags_search.html'
