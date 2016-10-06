from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from backend_candidate.views import HelpFindingCandidates


admin.autodiscover()
admin.site.site_header = getattr(settings, 'ADMIN_HEADER', 'Vota Inteligente')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'votainteligente.views.home', name='home'),
    # url(r'^votainteligente/', include('votainteligente.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('elections.urls')),
    (r'^preguntales/', include('preguntales.urls')),
    (r'^propuestas/', include('popular_proposal.urls', namespace='popular_proposals')),
    ('^pages/', include('django.contrib.flatpages.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^newsletter/', include('newsletter.urls')),
    (r'^api/', include('popolorest.urls')),
    (r'^backend_staff/', include('backend_staff.urls', namespace='backend_staff')),
    (r'^perfil_ciudadano/', include('backend_citizen.urls', namespace='backend_citizen')),
    (r'^candidatos/', include('backend_candidate.urls', namespace='backend_candidate')),
    url(r'^ayudanos/$',
        HelpFindingCandidates.as_view(),
        name='help'),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^accounts/passwordchange/?$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'registration/password_change.html'},
        name='password_reset'),
    url(r'^accounts/passwordchange/done/?$',
        'django.contrib.auth.views.password_change_done',
        {'template_name': 'registration/password_change_done_.html'},
        name='password_change_done'),
)

urlpatterns += patterns('',
                        url('', include('social.apps.django_app.urls', namespace='social'))
                        )

from django.conf import settings
if settings.THEME:
    urlpatterns += patterns('',
        ('^theme/', include('%s.urls' % (settings.THEME)))
        )

