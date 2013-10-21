from django.conf.urls import patterns, include, url
from tastypie.api import Api
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from elections.api import NewAnswerWebHook


admin.autodiscover()




urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'votainteligente.views.home', name='home'),
    # url(r'^votainteligente/', include('votainteligente.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('elections.urls')),
    ('^pages/', include('django.contrib.flatpages.urls')),
    (r'^tinymce/', include('tinymce.urls')),
)

v1_api = Api(api_name='v1')
v1_api.register(NewAnswerWebHook())

urlpatterns += patterns('',
  # ...more URLconf bits here...
  # Then add:
  (r'^api/', include(v1_api.urls)),
)