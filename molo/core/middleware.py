import uuid

from bs4 import BeautifulSoup

from django.http import HttpResponseForbidden
from django.views.defaults import permission_denied

from django_cas_ng.middleware import CASMiddleware
from django_cas_ng.views import login as cas_login, logout as cas_logout
from django.contrib.auth.views import login, logout
from django.conf import settings
# test
from django.contrib.messages import get_messages
from django.utils.translation import activate

from google_analytics.utils import build_ga_params, set_cookie
from google_analytics.tasks import send_ga_tracking

from molo.core.models import SiteSettings
from wagtail.wagtailcore.models import Site, Page
from django.core.urlresolvers import resolve
from django.shortcuts import redirect
from molo.core.models import Languages


class MoloCASMiddleware(CASMiddleware):

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func == login or view_func == logout:
            return None

        if view_func == cas_login:
            return cas_login(request, *view_args, **view_kwargs)
        elif view_func == cas_logout:
            return cas_logout(request, *view_args, **view_kwargs)

        if settings.CAS_ADMIN_PREFIX:
            if not request.path.startswith(settings.CAS_ADMIN_PREFIX):
                return None
        elif not view_func.__module__.startswith('django.contrib.admin.'):
            return None

        if request.user.is_authenticated():
            if request.user.has_perm('wagtailadmin.access_admin'):
                """
                Implemented using wagtails permissions model
                https://github.com/torchbox/wagtail/blob/master/wagtail/wagtailadmin/views/account.py#L112 # noqa
                """
                return None
            else:
                return permission_denied(request, 'error')
        return super(MoloCASMiddleware, self).process_view(
            request, view_func, view_args, view_kwargs)


class Custom403Middleware(object):
    """Catches 403 responses and raises 403 which allows for custom 403.html"""
    def process_response(self, request, response):
        storage = get_messages(request)
        for message in storage:
            pass
        if isinstance(response, HttpResponseForbidden):
            return permission_denied(request, 'error')
        return response


class ForceDefaultLanguageMiddleware(object):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via
    sessions or cookies

    Should be installed *before* any middleware that checks
    request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware
    """
    def process_request(self, request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']


class AdminLocaleMiddleware(object):
    """Ensures that the admin locale doesn't change with user selection"""
    def process_request(self, request):
        if request.path.startswith('/admin/') or \
           request.path.startswith('/django-admin/'):
            activate(settings.ADMIN_LANGUAGE_CODE)


class NoScriptGASessionMiddleware(object):
    """Store a unique session key for use with GTM"""
    def process_request(self, request):
        if 'MOLO_GA_SESSION_FOR_NOSCRIPT' not in request.session:
            request.session[
                'MOLO_GA_SESSION_FOR_NOSCRIPT'] = uuid.uuid4().hex


class MoloGoogleAnalyticsMiddleware(object):
    """Uses GA IDs stored in Wagtail to track pageviews using celery"""
    def submit_tracking(self, account, request, response):
        try:
            title = BeautifulSoup(
                response.content, "html.parser"
            ).html.head.title.text.encode('utf-8')
        except:
            title = None

        path = request.path
        referer = request.META.get('HTTP_REFERER', '')
        params = build_ga_params(
            request, account, path=path, referer=referer, title=title)
        response = set_cookie(params, response)
        send_ga_tracking.delay(params)
        return response

    def process_response(self, request, response):
        if hasattr(settings, 'GOOGLE_ANALYTICS_IGNORE_PATH'):
            exclude = [p for p in settings.GOOGLE_ANALYTICS_IGNORE_PATH
                       if request.path.startswith(p)]
            if any(exclude):
                return response

        # Only track 200 responses. Non 200 responses don't have `request.site`
        if not response.status_code == 200:
            return response

        site_settings = SiteSettings.for_site(request.site)
        local_ga_account = site_settings.local_ga_tracking_code or \
            settings.GOOGLE_ANALYTICS.get('google_analytics_id')

        if local_ga_account:
            response = self.submit_tracking(
                local_ga_account, request, response)

        if site_settings.global_ga_tracking_code:
            response = self.submit_tracking(
                site_settings.global_ga_tracking_code, request, response)

        return response


class MultiSiteRedirectToHomepage(object):

    def process_request(self, request):
        if request.path.startswith('/admin/pages/'):
            current_site = Site.find_for_request(request)
            func, args, kwargs = resolve(request.path)
            if args:
                p_site = Page.objects.get(pk=args[-1]).get_site()
                if p_site and not current_site == p_site:
                    return redirect('%s%s' % (p_site.root_url, request.path))
            if not Languages.for_site(request.site).languages.all().exists():
                return redirect('%s/admin/' % request.site.root_url)
