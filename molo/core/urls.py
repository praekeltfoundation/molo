from django.conf.urls import include, re_path
from django.views.decorators.cache import never_cache

from wagtail.utils.urlpatterns import decorate_urlpatterns
from wagtail.images.views.serve import ServeView

from .api.urls import api_router
from . import views


urlpatterns = [
    re_path(
        r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$',
        ServeView.as_view(),
        name='wagtailimages_serve'
    ),
    re_path(r'^search/$', views.search, name='search'),
    re_path(
        r'^locale/(?P<locale>[\w\-\_]+)/$',
        views.locale_set,
        name='locale_set'
    ),
    re_path(
        r'^health/$',
        views.health,
        name='health'
    ),
    re_path(
        r'^home-index/$',
        views.home_index,
        name='home_index'
    ),
    re_path(
        r'^section-index/$',
        views.section_index,
        name='section_index'
    ),
    re_path(
        r'^search-index/$',
        views.search_index,
        name='search_index'
    ),
    re_path(
        r'^tag-index/$',
        views.tag_index,
        name='tag_index'
    ),
    re_path(
        r'^home-more/$',
        views.home_more,
        name='home_more'
    ),
    re_path(r'^api/', include(
        ('molo.core.api.urls', 'molo.api'), namespace='molo_api')),

    re_path(r'^api/v2/', include((
        decorate_urlpatterns(api_router.get_urlpatterns(), never_cache),
        'molo.api'), namespace=api_router.url_namespace
    )),
    re_path(
        r'^versions/$',
        views.versions,
        name='versions'),
    re_path(r'^djga/', include('google_analytics.urls')),
    re_path(
        r'^tags/(?P<tag_name>[\w-]+)/$',
        views.TagsListView.as_view(),
        name='tags_list'
    ),
    re_path(r'^(\d+)/publish/$', views.publish, name='publish'),
    re_path(
        r'^(\d+)/copy_to_all_confirm/$',
        views.copy_to_all_confirm, name='copy-to-all-confirm'),
    re_path(
        r'^(\d+)/copy_to_all/$',
        views.copy_to_all, name='copy-to-all'),
    re_path('', include('django_prometheus.urls')),
]
