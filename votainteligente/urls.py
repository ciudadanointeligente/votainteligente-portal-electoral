from django.conf.urls import include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from backend_candidate.views import HelpFindingCandidates
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import password_change, password_change_done, login
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from votainteligente.sitemaps  import ElectionsSitemap, CandidatesSitemap, ProposalSitemap
from votainteligente.rest_api_router import router
from django.utils.translation import ugettext_lazy as _
admin.autodiscover()
admin.site.site_header = getattr(settings, 'ADMIN_HEADER', 'Vota Inteligente')


sitemaps = {
    'elections': ElectionsSitemap,
    'candidates': CandidatesSitemap,
    'proposals': ProposalSitemap,
}

urlpatterns = [
    # Examples:
    # url(r'^$', 'votainteligente.views.home', name='home'),
    # url(r'^votainteligente/', include('votainteligente.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('elections.urls')),
    url(_(r'^propuestas/'), include('popular_proposal.urls', namespace='popular_proposals')),
    url(_('^pages/'), include('django.contrib.flatpages.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^backend_staff/', include('backend_staff.urls', namespace='backend_staff')),
    url(_(r'^perfil_ciudadano/'), include('backend_citizen.urls', namespace='backend_citizen')),
    url(r'^suggestions/', include('suggestions_for_candidates.urls', namespace='suggestions_for_candidates')),
    url(_(r'^media_naranja/'), include('medianaranja2.urls', namespace='medianaranja2')),
    url(_(r'^organizacion/'), include('organization_profiles.urls', namespace='organization_profiles')),
    url(_(r'^candidatos/'), include('backend_candidate.urls', namespace='backend_candidate')),
    url(r'^proposal_subscriptions/', include('proposal_subscriptions.urls', namespace='proposal_subscriptions')),
    url(_(r'^ayudanos/$'),
        HelpFindingCandidates.as_view(),
        name='help'),
    url(_(r'^encuentro_ciudadano/$'),
        TemplateView.as_view(template_name='encuentro_ciudadano.html'),
        name='encuentro_ciudadano'),
    url(_(r'^que_es/$'),
        TemplateView.as_view(template_name='que_es.html'),
        name='que_es'),
    url(_(r'^material_ciudadano/$'),
        TemplateView.as_view(template_name='material_ciudadano.html'),
        name='material_ciudadano'),
    url(r'^cores/$',
        TemplateView.as_view(template_name='cores.html'),
        name='cores'),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^accounts/login/organizacion/?$',
        login,
        {'template_name': 'registration/login_organizacion.html'},
        name='login_users'),
    url(r'^accounts/login/usuario_y_password/?$',
        login,
        {'template_name': 'registration/login_username_and_password.html'},
        name='username_and_password'),
    url(r'^accounts/passwordchange/?$',
        password_change,
        {'template_name': 'registration/password_change.html'},
        name='password_reset'),
    url(r'^accounts/passwordchange/done/?$',
        password_change_done,
        {'template_name': 'registration/password_change_done_.html'},
        name='password_change_done'),
    url(r'^api/', include(router.urls)),
    url(r'^robots\.txt', include('robots.urls')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}),

]

urlpatterns += [
                        url('', include('social_django.urls', namespace='social'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.THEME:
    urlpatterns += [
        url('^theme/', include('%s.urls' % (settings.THEME)))
    ]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
