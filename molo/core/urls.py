from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from . import molo_import_view


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

    url(r'^api-auth/', include(
        'rest_framework.urls', namespace='rest_framework')),

    url(
        r'^repos/$',
        molo_import_view.get_repos,
        name='get_repos'
    ),

    url(
        r'^repos/(?P<name>[\w-]+)/$',
        molo_import_view.get_content_for_repo,
        name='get_repos_content'
    ),
    url(
        r'^repos/(?P<name>[\w-]+)/import/',
        molo_import_view.import_content,
        name='import_content'
    ),
)
