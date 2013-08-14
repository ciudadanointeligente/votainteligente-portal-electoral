from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from haystack.views import SearchView
from elections.forms import ElectionForm

urlpatterns = patterns('',
	url(r'^/?$', TemplateView.as_view(template_name='elections/home.html'), name='home' ),
	url(r'^buscar/?$', SearchView(
	        template='search.html',
	        form_class=ElectionForm
	    ), name='search' ),
)