from django.conf.urls import include, url
from django.views.decorators.cache import never_cache

from wagtail.utils.urlpatterns import decorate_urlpatterns
from wagtail.wagtailimages.views.serve import ServeView

from .api.urls import api_router
from . import views


urlpatterns = [
    url(
        r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$',
        ServeView.as_view(),
        name='wagtailimages_serve'
    ),
    url(r'^search/$', views.search, name='search'),
    url(
        r'^locale/(?P<locale>[\w\-\_]+)/$',
        views.locale_set,
        name='locale_set'
    ),
    url(
        r'^health/$',
        views.health,
        name='health'
    ),
    url(
        r'^home-index/$',
        views.home_index,
        name='home_index'
    ),
    url(
        r'^section-index/$',
        views.section_index,
        name='section_index'
    ),
    url(
        r'^search-index/$',
        views.search_index,
        name='search_index'
    ),
    url(
        r'^tag-index/$',
        views.tag_index,
        name='tag_index'
    ),
    url(
        r'^home-more/$',
        views.home_more,
        name='home_more'
    ),
    url(r'^reaction/(?P<article_slug>[0-9A-Za-z_\-]+)/'
        '(?P<question_id>\d+)/vote/$',
        views.ReactionQuestionChoiceView.as_view(),
        name='reaction-vote'),
    url(r'^reaction/(?P<article_slug>[0-9A-Za-z_\-]+)/'
        '(?P<question_id>\d+)/(?P<choice_slug>[0-9A-Za-z_\-]+)/feedback/$',
        views.ReactionQuestionChoiceFeedbackView.as_view(),
        name='reaction-feedback'),

    url(r'^api/', include(
        'molo.core.api.urls', namespace='molo_api')),

    url(r'^api/v2/', include(
        decorate_urlpatterns(api_router.get_urlpatterns(), never_cache),
        namespace=api_router.url_namespace
    )),
    url(
        r'^versions/$',
        views.versions,
        name='versions'),
    url(r'^djga/', include('google_analytics.urls')),
    url(
        r'^tags/(?P<tag_name>[\w-]+)/$',
        views.TagsListView.as_view(),
        name='tags_list'
    ),
    url(r'^(\d+)/publish/$', views.publish, name='publish'),
    url(
        r'^(\d+)/copy_to_all_confirm/$',
        views.copy_to_all_confirm, name='copy-to-all-confirm'),
    url(
        r'^(\d+)/copy_to_all/$',
        views.copy_to_all, name='copy-to-all'),
]
