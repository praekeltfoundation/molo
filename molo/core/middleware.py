
from django.http import HttpResponseForbidden
from django.views.defaults import permission_denied

from django_cas_ng.middleware import CASMiddleware
from django_cas_ng.views import login as cas_login, logout as cas_logout


class MoloCASMiddleware(CASMiddleware):

    def process_view(self, request, view_func, view_args, view_kwargs):

        if view_func == cas_login:
            return cas_login(request, *view_args, **view_kwargs)
        elif view_func == cas_logout:
            return cas_logout(request, *view_args, **view_kwargs)

        if request.user.is_authenticated():
            if request.user.is_staff:
                return None
            else:
                return permission_denied(request)

        return super(MoloCASMiddleware, self).process_view(
            request, view_func, view_args, view_kwargs)


class Custom403Middleware(object):
    """Catches 403 responses and raises 403 which allows for custom 403.html"""
    def process_response(self, request, response):
        if isinstance(response, HttpResponseForbidden):
            return permission_denied(request)
        return response
