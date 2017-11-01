from django.conf.urls import patterns, include, url

from wagtail.wagtailimages.views.serve import ServeView

from .views import (
    search, TagsListView, ReactionQuestionChoiceView,
    ReactionQuestionChoiceFeedbackView, publish)


urlpatterns = patterns(
    '',
    url(
        r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$',
        ServeView.as_view(),
        name='wagtailimages_serve'
    ),
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
    url(
        r'^home-index/$',
        'molo.core.views.home_index',
        name='home_index'
    ),
    url(
        r'^section-index/$',
        'molo.core.views.section_index',
        name='section_index'
    ),
    url(
        r'^search-index/$',
        'molo.core.views.search_index',
        name='search_index'
    ),
    url(
        r'^tag-index/$',
        'molo.core.views.tag_index',
        name='tag_index'
    ),
    url(
        r'^home-more/$',
        'molo.core.views.home_more',
        name='home_more'
    ),
    url(r'^reaction/(?P<article_slug>[0-9A-Za-z_\-]+)/'
        '(?P<question_id>\d+)/vote/$',
        ReactionQuestionChoiceView.as_view(),
        name='reaction-vote'),
    url(r'^reaction/(?P<article_slug>[0-9A-Za-z_\-]+)/'
        '(?P<question_id>\d+)/(?P<choice_slug>[0-9A-Za-z_\-]+)/feedback/$',
        ReactionQuestionChoiceFeedbackView.as_view(),
        name='reaction-feedback'),
    url(r'^import/', include(
        'molo.core.content_import.urls', namespace='content_import')),

    url(r'^api/', include(
        'molo.core.api.urls', namespace='molo_api')),

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
    url(r'^(\d+)/publish/$', publish, name='publish'),
)
