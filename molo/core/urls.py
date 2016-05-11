from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
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
)
