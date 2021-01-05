import os

from django.conf.urls import include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView
from django_cas_ng import views as cas_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls

from molo.core import views as core_views
# Path to a custom template that will be used by the admin
# site main index view.
admin.site.index_template = 'django_admin/index.html'
admin.autodiscover()

# implement CAS URLs in a production setting
if settings.ENABLE_SSO:
    urlpatterns = [
        re_path(
            r'^admin/login/',
            cas_views.LoginView.as_view(), name='cas_ng_login'),
        re_path(
            r'^admin/logout/',
            cas_views.LogoutView.as_view(), name='cas_ng_logout'),
        re_path(
            r'^admin/callback/',
            cas_views.CallbackView.as_view(), name='cas_ng_callback'), ]
else:
    urlpatterns = []

urlpatterns += [
    re_path(
        r'^django-admin/upload_media/', core_views.upload_file,
        name='molo_upload_media'),
    re_path(
        r'^django-admin/download_media/', core_views.download_file,
        name='molo_download_media'),
    re_path(r'^django-admin/', admin.site.urls),
    re_path(r'^admin/', include(wagtailadmin_urls)),
    re_path(r'^documents/', include(wagtaildocs_urls)),
    re_path(r'^robots\.txt$', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain')),
    re_path(r'^sitemap\.xml$', core_views.sitemap),

{% for app_name, regex in cookiecutter.include %}
    re_path(
        r'{{regex}}',
        include((
            '{{app_name}}.urls',
            '{{app_name}}'),
            namespace='{{app_name}}')
    ),
{% endfor %}
    re_path(r"^mote/", include("mote.urls", namespace="mote")),
    re_path(r'', include('molo.core.urls')),
    re_path(r'^profiles/', include((
        'molo.profiles.urls', 'molo.profiles'), namespace='molo.profiles')),
    re_path('^', include('django.contrib.auth.urls')),
    re_path(r'', include(wagtail_urls)),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL + 'images/',
        document_root=os.path.join(settings.MEDIA_ROOT, 'images'))
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
