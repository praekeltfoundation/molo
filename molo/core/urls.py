from django.conf.urls import patterns, url

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
)
