import os

from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView
from django_cas_ng import views as cas_views
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.contrib.wagtailsitemaps import views as wagtail_views

from molo.core import views as core_views
# Path to a custom template that will be used by the admin
# site main index view.
admin.site.index_template = 'django_admin/index.html'
admin.autodiscover()

# implement CAS URLs in a production setting
if settings.ENABLE_SSO:
    urlpatterns = [
        url(r'^admin/login/', cas_views.login),
        url(r'^admin/logout/', cas_views.logout),
        url(r'^admin/callback/', cas_views.callback),
    ]
else:
    urlpatterns = []

urlpatterns += [
    url(r'^django-admin/upload_media/', core_views.upload_file,
        name='molo_upload_media'),
    url(r'^django-admin/download_media/', core_views.download_file,
        name='molo_download_media'),
    url(r'^django-admin/', include(admin.site.urls)),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^robots\.txt$', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain')),
    url(r'^sitemap\.xml$', wagtail_views.sitemap),

{% for app_name, regex in cookiecutter.include %}
    url(r'{{regex}}',
        include('{{app_name}}.urls',
                namespace='{{app_name}}',
                app_name='{{app_name}}')),
{% endfor %}
    url(r"^mote/", include("mote.urls", namespace="mote")),
    url(r'', include('molo.core.urls')),
    url(r'^profiles/', include(
        'molo.profiles.urls',
        namespace='molo.profiles', app_name='molo.profiles')),
    url('^', include('django.contrib.auth.urls')),
    url(r'', include(wagtail_urls)),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL + 'images/',
        document_root=os.path.join(settings.MEDIA_ROOT, 'images'))
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
