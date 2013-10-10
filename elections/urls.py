from django.conf import settings
from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from haystack.views import SearchView
from elections.forms import ElectionForm
from elections.views import ElectionsSearchByTagView, HomeView, ElectionDetailView,\
							CandidateDetailView, SoulMateDetailView

media_root = getattr(settings, 'MEDIA_ROOT', '/') 

urlpatterns = patterns('',
	url(r'^/?$', HomeView.as_view(template_name='elections/home.html'), name='home' ),
	url(r'^buscar/?$', SearchView(
	        template='search.html',
	        form_class=ElectionForm
	    ), name='search' ),
	url(r'^busqueda_tags/?$', ElectionsSearchByTagView.as_view(), name='tags_search' ),
	url(r'^election/(?P<slug>[-\w]+)/?$', 
		ElectionDetailView.as_view(template_name='elections/election_detail.html'), 
		name='election_view' ),
	url(r'^election/(?P<slug>[-\w]+)/questionary/?$',
		ElectionDetailView.as_view(template_name='elections/election_questionary.html'), 
		name='questionary_detail_view'),
	#compare two candidates
	url(r'^election/(?P<slug>[-\w]+)/face-to-face/(?P<slug_candidate_one>[-\w]+)/(?P<slug_candidate_two>[-\w]+)/?$',
		ElectionDetailView.as_view(template_name='elections/compare_candidates.html'), 
		name='face_to_face_two_candidates_detail_view'),
	#one candidate for compare
	url(r'^election/(?P<slug>[-\w]+)/face-to-face/(?P<slug_candidate_one>[-\w]+)/?$',
		ElectionDetailView.as_view(template_name='elections/compare_candidates.html'), 
		name='face_to_face_one_candidate_detail_view'),
	#no one candidate
	url(r'^election/(?P<slug>[-\w]+)/face-to-face/?$',
		ElectionDetailView.as_view(template_name='elections/compare_candidates.html'), 
		name='face_to_face_no_candidate_detail_view'),
	#soulmate
	url(r'^election/(?P<slug>[-\w]+)/soul-mate/?$',
		SoulMateDetailView.as_view(template_name='elections/soulmate_candidate.html'), 
		name='soul_mate_detail_view'),
	#ask
	url(r'^election/(?P<slug>[-\w]+)/ask/?$',
		ElectionDetailView.as_view(template_name='elections/ask_candidate.html'), 
		name='ask_detail_view'),
	#ranking
	url(r'^election/(?P<slug>[-\w]+)/ranking/?$',
		ElectionDetailView.as_view(template_name='elections/ranking_candidates.html'), 
		name='ranking_detail_view'),
	url(r'^election/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/?$', 
		CandidateDetailView.as_view(template_name='elections/candidate_detail.html'),
		name='candidate_detail_view'
		),
	url(r'^election/(?P<slug>[-\w]+)/extra_info.html$',
		ElectionDetailView.as_view(template_name='elections/extra_info.html'), 
		name='election_extra_info'),
)

urlpatterns += patterns('', 
	url(r'^cache/(?P<path>.*)$','django.views.static.serve',
    	{'document_root': media_root})
)