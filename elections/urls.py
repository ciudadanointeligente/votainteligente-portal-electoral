from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from haystack.views import SearchView
from elections.forms import ElectionForm
from elections.views import ElectionsSearchByTagView, HomeView

urlpatterns = patterns('',
	url(r'^/?$', HomeView.as_view(template_name='elections/home.html'), name='home' ),
	url(r'^buscar/?$', SearchView(
	        template='search.html',
	        form_class=ElectionForm
	    ), name='search' ),
	url(r'^busqueda_tags/?$', ElectionsSearchByTagView.as_view(), name='tags_search' ),
)