from django.conf.urls import include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from backend_candidate.views import HelpFindingCandidates
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import password_change, password_change_done, login
from django.conf.urls.static import static


admin.autodiscover()
admin.site.site_header = getattr(settings, 'ADMIN_HEADER', 'Vota Inteligente')

urlpatterns = [
    # Examples:
    # url(r'^$', 'votainteligente.views.home', name='home'),
    # url(r'^votainteligente/', include('votainteligente.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('elections.urls')),
    url(r'^preguntales/', include('preguntales.urls')),
    url(r'^propuestas/', include('popular_proposal.urls', namespace='popular_proposals')),
    url('^pages/', include('django.contrib.flatpages.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^newsletter/', include('newsletter.urls')),
    url(r'^backend_staff/', include('backend_staff.urls', namespace='backend_staff')),
    url(r'^perfil_ciudadano/', include('backend_citizen.urls', namespace='backend_citizen')),
    url(r'^organizacion/', include('organization_profiles.urls', namespace='organization_profiles')),
    url(r'^candidatos/', include('backend_candidate.urls', namespace='backend_candidate')),
    url(r'^proposal_subscriptions/', include('proposal_subscriptions.urls', namespace='proposal_subscriptions')),
    url(r'^ayudanos/$',
        HelpFindingCandidates.as_view(),
        name='help'),
    url(r'^compromisos/$',
        TemplateView.as_view(template_name='compromisos_electos.html'),
        name='compromisos'),
    url(r'^meetup/$',
        TemplateView.as_view(template_name='meetup.html'),
        name='meetup'),
    url(r'^encuentroONGs/$',
        TemplateView.as_view(template_name='encuentroONGs.html'),
        name='encuentroONGs'),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^accounts/login/ciudadanos/?$',
        login,
        {'template_name': 'registration/login_citizens.html'},
        name='login_users'),
    url(r'^accounts/passwordchange/?$',
        password_change,
        {'template_name': 'registration/password_change.html'},
        name='password_reset'),
    url(r'^accounts/passwordchange/done/?$',
        password_change_done,
        {'template_name': 'registration/password_change_done_.html'},
        name='password_change_done'),
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
