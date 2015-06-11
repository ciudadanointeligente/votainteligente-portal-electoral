from django.conf import settings
from django.conf.urls import patterns, url
from haystack.views import SearchView
from elections.forms import ElectionForm
from elections.views import ElectionsSearchByTagView, HomeView, ElectionDetailView,\
    CandidateDetailView, SoulMateDetailView, FaceToFaceView, AreaDetailView
from sitemaps import *

from django.views.decorators.cache import cache_page

media_root = getattr(settings, 'MEDIA_ROOT', '/')


sitemaps = {
    'elections': ElectionsSitemap,
    'candidates': CandidatesSitemap,
}

urlpatterns = patterns('',
    url(r'^/?$', cache_page(60 * settings.CACHE_MINUTES)(HomeView.as_view(template_name='elections/home.html')), name='home'),
    url(r'^buscar/?$', SearchView(template='search.html',
            form_class=ElectionForm), name='search'),
    url(r'^busqueda_tags/?$', ElectionsSearchByTagView.as_view(), name='tags_search'),
    url(r'^election/(?P<slug>[-\w]+)/?$',
        cache_page(60 * settings.CACHE_MINUTES)(ElectionDetailView.as_view(template_name='elections/election_detail.html')),
        name='election_view'),
    url(r'^election/(?P<slug>[-\w]+)/questionary/?$',
        cache_page(60 * settings.CACHE_MINUTES)(ElectionDetailView.as_view(template_name='elections/election_questionary.html')),
        name='questionary_detail_view'),
    #compare two candidates
    url(r'^election/(?P<slug>[-\w]+)/face-to-face/(?P<slug_candidate_one>[-\w]+)/(?P<slug_candidate_two>[-\w]+)/?$',
        cache_page(60 * settings.CACHE_MINUTES)(FaceToFaceView.as_view(template_name='elections/compare_candidates.html')),
        name='face_to_face_two_candidates_detail_view'),
    #one candidate for compare
    url(r'^election/(?P<slug>[-\w]+)/face-to-face/(?P<slug_candidate_one>[-\w]+)/?$',
        cache_page(60 * settings.CACHE_MINUTES)(ElectionDetailView.as_view(template_name='elections/compare_candidates.html')),
        name='face_to_face_one_candidate_detail_view'),
    #no one candidate
    url(r'^election/(?P<slug>[-\w]+)/face-to-face/?$',
        cache_page(60 * settings.CACHE_MINUTES)(ElectionDetailView.as_view(template_name='elections/compare_candidates.html')),
        name='face_to_face_no_candidate_detail_view'),
    #soulmate
    url(r'^election/(?P<slug>[-\w]+)/soul-mate/?$',
        SoulMateDetailView.as_view(template_name='elections/soulmate_candidate.html'),
        name='soul_mate_detail_view'),
    url(r'^election/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/?$',
        cache_page(60 * settings.CACHE_MINUTES)(CandidateDetailView.as_view(template_name='elections/candidate_detail.html')),
        name='candidate_detail_view'
        ),
    url(r'^election/(?P<slug>[-\w]+)/extra_info.html$',
        ElectionDetailView.as_view(template_name='elections/extra_info.html'),
        name='election_extra_info'),
    url(r'^area/(?P<slug>[-\w]+)/?$',
        AreaDetailView.as_view(template_name='elections/area.html'),
        name='area'),

    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

urlpatterns += patterns('',
    url(r'^cache/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': media_root})
)
