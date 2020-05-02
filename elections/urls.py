from django.conf import settings
from django.conf.urls import url
from haystack.views import SearchView
from elections.forms import ElectionForm
from elections.views import (
    ElectionsSearchByTagView,
    HomeView,
    ElectionDetailView,
    CandidateDetailView,
    FaceToFaceView,
    AreaDetailView,
    KnowYourCandidatesView,
    )

from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.cache import cache_page


media_root = getattr(settings, 'MEDIA_ROOT', '/')




urlpatterns = [
    url(r'^$', cache_page(60 * settings.CACHE_MINUTES)(xframe_options_exempt(HomeView.as_view())), name='home'),
    url(r'^buscar/?$', SearchView(template='search.html',
            form_class=ElectionForm), name='search'),
    url(r'^busqueda_tags/?$', ElectionsSearchByTagView.as_view(), name='tags_search'),
    url(r'^eleccion/(?P<slug>[-\w]+)/?$',
        cache_page(60 * settings.CACHE_MINUTES)(ElectionDetailView.as_view(template_name='elections/election_detail.html')),
        name='election_view'),
    url(r'^eleccion/(?P<slug>[-\w]+)/questionary/?$',
        cache_page(60 * settings.CACHE_MINUTES)(ElectionDetailView.as_view(template_name='elections/election_questionary.html')),
        name='questionary_detail_view'),
    #compare two candidates
    url(r'^eleccion/(?P<slug>[-\w]+)/face-to-face/(?P<slug_candidate_one>[-\w]+)/(?P<slug_candidate_two>[-\w]+)/?$',
        cache_page(60 * settings.CACHE_MINUTES)(FaceToFaceView.as_view(template_name='elections/compare_candidates.html')),
        name='face_to_face_two_candidates_detail_view'),
    #one candidate for compare
    url(r'^eleccion/(?P<slug>[-\w]+)/face-to-face/(?P<slug_candidate_one>[-\w]+)/?$',
        cache_page(60 * settings.CACHE_MINUTES)(ElectionDetailView.as_view(template_name='elections/compare_candidates.html')),
        name='face_to_face_one_candidate_detail_view'),
    #no one candidate
    url(r'^eleccion/(?P<slug>[-\w]+)/face-to-face/?$',
        cache_page(60 * settings.CACHE_MINUTES)(ElectionDetailView.as_view(template_name='elections/compare_candidates.html')),
        name='face_to_face_no_candidate_detail_view'),

    url(r'^eleccion/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/?$',
        cache_page(60 * settings.CACHE_MINUTES)(CandidateDetailView.as_view(template_name='elections/candidate_detail.html')),
        name='candidate_detail_view'
        ),
    url(r'^candidaturas/(?P<area_slug>[-\w]+)/(?P<slug>[-\w]+)/?$',
        cache_page(60 * settings.CACHE_MINUTES)(CandidateDetailView.as_view(template_name='elections/candidate_detail.html')),
        name='candidate_detail_view_area'
        ),
    url(r'^eleccion/(?P<slug>[-\w]+)/extra_info.html$',
        ElectionDetailView.as_view(template_name='elections/extra_info.html'),
        name='election_extra_info'),
    url(r'^candidaturas/(?P<slug>[-\w]+)/?$',
        AreaDetailView.as_view(template_name='elections/area.html'),
        name='area'),
    url(r'^ayudanos/(?P<slug>[-\w]+)/?$',
        ElectionDetailView.as_view(template_name='elections/ayudanos.html'),
        name='help_election'),
    url(r'^candidaturas/?$', KnowYourCandidatesView.as_view(), name='know_your_candidates'),
    
]

# urlpatterns += [
#     url(r'^cache/(?P<path>.*)$', sitemap,
#         {'document_root': media_root})
# ]
