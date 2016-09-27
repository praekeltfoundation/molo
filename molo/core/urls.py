from django.conf.urls import patterns, include, url

from .views import search


urlpatterns = patterns(
    '',
    url(r'search/$', search, name='search'),
    url(
        r'^locale/(?P<locale>[\w\-\_]+)/$',
        'molo.core.views.locale_set',
        name='locale_set'
    ),

    url(
        r'^health/$',
        'molo.core.views.health',
        name='health'
    ),

    url(r'^import/', include(
        'molo.core.content_import.urls', namespace='content_import')),
    url(
        r'^versions/$',
        'molo.core.views.versions',
        name='versions'),
    url(r'^djga/', include('google_analytics.urls')),
)
