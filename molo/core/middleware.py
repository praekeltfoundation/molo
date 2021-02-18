import uuid
import django.utils.deprecation

from bs4 import BeautifulSoup

from django.conf import settings
from django.http import HttpResponseForbidden
from django_cas_ng.middleware import CASMiddleware
from django.views.defaults import permission_denied
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import resolve, reverse
from django.shortcuts import redirect, render, get_object_or_404
from django_cas_ng.views import LoginView as CasLogin,\
    LogoutView as CasLogout
from django.utils.translation import activate
from django.contrib.messages import get_messages
from django.utils.translation import get_language_from_request

from google_analytics.tasks import send_ga_tracking
from google_analytics.utils import build_ga_params, set_cookie

from wagtail.core.models import Site, Page
from molo.core.models import SiteSettings, Languages


class MoloCASMiddleware(CASMiddleware):

    def process_view(self, request, view_func, view_args, view_kwargs):
        logout = LogoutView.as_view().__name__
        is_logout = view_func.__name__ == logout
        is_login = view_func.__name__ == LoginView.as_view().__name__

        if is_login or is_logout:
            return None

        if view_func.__name__ == CasLogin.__name__:
            return CasLogin(request, *view_args, **view_kwargs)
        elif is_logout:
            return CasLogout.as_view(request, *view_args, **view_kwargs)

        if settings.CAS_ADMIN_PREFIX:
            if not request.path.startswith(settings.CAS_ADMIN_PREFIX):
                return None
        elif not view_func.__module__.startswith('django.contrib.admin.'):
            return None

        if request.user.is_authenticated:
            if request.user.has_perm('wagtailadmin.access_admin'):
                """
                Implemented using wagtails permissions model
                https://github.com/torchbox/wagtail/blob/master/wagtail/wagtailadmin/views/account.py#L112 # noqa
                """
                return None
            else:
                return permission_denied(request, HttpResponseForbidden)
        return super(MoloCASMiddleware, self).process_view(
            request, view_func, view_args, view_kwargs)


class Custom403Middleware(django.utils.deprecation.MiddlewareMixin):
    """Catches 403 responses and raises 403 which allows for custom 403.html"""
    def process_response(self, request, response):
        storage = get_messages(request)
        for message in storage:
            pass
        if isinstance(response, HttpResponseForbidden):
            return permission_denied(request, HttpResponseForbidden)
        return response


class ForceDefaultLanguageMiddleware(django.utils.deprecation.MiddlewareMixin):
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


class AdminLocaleMiddleware(django.utils.deprecation.MiddlewareMixin):
    """Ensures that the admin locale doesn't change with user selection"""
    def process_request(self, request):
        if request.path.startswith('/admin/') or \
           request.path.startswith('/django-admin/'):
            activate(settings.ADMIN_LANGUAGE_CODE)


class NoScriptGASessionMiddleware(django.utils.deprecation.MiddlewareMixin):
    """Store a unique session key for use with GTM"""
    def process_request(self, request):
        if 'MOLO_GA_SESSION_FOR_NOSCRIPT' not in request.session:
            request.session[
                'MOLO_GA_SESSION_FOR_NOSCRIPT'] = uuid.uuid4().hex


class SetLangaugeCodeMiddleware(django.utils.deprecation.MiddlewareMixin):
    """Sets the language code"""
    def process_response(self, request, response):
        if 'locale' not in request.path:
            return response
        locale_code = request.path.split("/")[2]
        response.set_cookie('django_language', locale_code)
        return response


class SetSiteMiddleware(django.utils.deprecation.MiddlewareMixin):
    """Sets the wagtail site"""
    def process_request(self, request):
        Site.find_for_request(request)


class MoloGoogleAnalyticsMiddleware(django.utils.deprecation.MiddlewareMixin):
    """Uses GA IDs stored in Wagtail to track pageviews using celery"""
    def submit_tracking(self, account, request, response, custom_params={}):
        try:
            title = BeautifulSoup(
                response.content, "html.parser"
            ).html.head.title.text.encode('utf-8')
        except:
            title = None

        path = request.get_full_path()
        custom_params['cd10'] = get_language_from_request(request)
        referer = request.META.get('HTTP_REFERER', '')
        if hasattr(request, 'user') and hasattr(request.user, 'profile')\
                and request.user.profile.uuid:
            uuid = request.user.profile.uuid
            params = build_ga_params(
                request, account, path=path,
                referer=referer, title=title,
                user_id=uuid, custom_params=custom_params)
        else:
            params = build_ga_params(
                request, account, path=path, referer=referer,
                title=title, custom_params=custom_params)

        # send user unique id after cookie's been set
        response = set_cookie(params, response)

        send_ga_tracking.delay(params)
        return response

    def process_response(self, request, response):
        if hasattr(settings, 'GOOGLE_ANALYTICS_IGNORE_PATH'):
            exclude = [p for p in settings.GOOGLE_ANALYTICS_IGNORE_PATH
                       if request.path.startswith(p)]
            if any(exclude):
                return response

        # Only track 200 and 302 responses for request.site
        if not (response.status_code == 200 or response.status_code == 302):
            return response

        site_settings = SiteSettings.for_site(Site.find_for_request(request))
        local_ga_account = site_settings.local_ga_tracking_code or \
            settings.GOOGLE_ANALYTICS.get('google_analytics_id')

        if local_ga_account:
            response = self.submit_tracking(
                local_ga_account, request, response)

        if site_settings.global_ga_tracking_code:
            response = self.submit_tracking(
                site_settings.global_ga_tracking_code, request, response)

        return response


class MultiSiteRedirectToHomepage(django.utils.deprecation.MiddlewareMixin):

    def process_request(self, request):
        if request.path.startswith('/admin/pages/') and \
                not request.path.startswith('/admin/pages/moderation/'):
            current_site = Site.find_for_request(request)
            func, args, kwargs = resolve(request.path)
            if args:
                p_site = get_object_or_404(
                    Page, pk=args[-1]).specific.get_site()
                if p_site and not current_site == p_site:
                    return redirect('%s%s' % (p_site.root_url, request.path))
            if not Languages.for_site(current_site).languages.all().exists():
                return redirect('%s/admin/' % current_site.root_url)


class MaintenanceModeMiddleware(django.utils.deprecation.MiddlewareMixin):

    def process_request(self, request):
        maintenance = getattr(settings, 'MAINTENANCE_MODE', None)
        template_name = getattr(
            settings,
            'MAINTENANCE_MODE_TEMPLATE', 'core/maintenance_mode.html'
        )
        if maintenance and reverse('health') not in request.path:
            page_ctx = getattr(
                settings,
                'MAINTENANCE_MODE_PAGE_CONTEXT',
                {'title': 'Maintenance Mode'}
            )

            class Page(object):
                depth = 2

                def __init__(self, ctx):
                    for k, v in ctx.items():
                        setattr(self, k, v)

            return render(
                request, template_name, context={
                    'self': Page(page_ctx),
                    'request': request,
                    'ENV': getattr(settings, 'ENV', 'dev'),
                    'STATIC_URL': getattr(settings, 'STATIC_URL', 'dev'),
                }
            )
