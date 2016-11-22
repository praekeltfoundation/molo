from django.conf.urls import patterns, include, url
from django.views.decorators.cache import never_cache

from wagtail.utils.urlpatterns import decorate_urlpatterns

from .content_import.api.urls import api_router
from .views import search, TagsListView


urlpatterns = patterns(
    '',
    url(r'^search/$', search, name='search'),
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

    url(r'^api/', include(
        'molo.core.content_import.api.urls', namespace='molo_api')),

    url(r'^api/v2/', include(
        decorate_urlpatterns(api_router.get_urlpatterns(), never_cache),
        namespace=api_router.url_namespace)
    ),

    url(
        r'^versions/$',
        'molo.core.views.versions',
        name='versions'),
    url(r'^djga/', include('google_analytics.urls')),
    url(
        r'^tags/(?P<tag_name>[\w-]+)/$',
        TagsListView.as_view(),
        name='tags_list'
    ),
)
