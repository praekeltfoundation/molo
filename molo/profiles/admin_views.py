from wagtail.contrib.modeladmin.views import IndexView
from wagtail.admin import messages
from django.utils.translation import ugettext as _
from django.shortcuts import redirect
from .task import send_export_email


class FrontendUsersAdminView(IndexView):
    def send_export_email_to_celery(self, email, arguments):
        send_export_email.delay(email, arguments)

    def post(self, request, *args, **kwargs):
        if not request.user.email:
            messages.error(
                request, _(
                    "Your email address is not configured. "
                    "Please update it before exporting."))
            return redirect(request.path)

        drf__date_joined__gte = request.GET.get('drf__date_joined__gte')
        drf__date_joined__lte = request.GET.get('drf__date_joined__lte')
        is_active_exact = request.GET.get('is_active__exact')

        filter_list = {
            'date_joined__range': (drf__date_joined__gte,
                                   drf__date_joined__lte) if
            drf__date_joined__gte and drf__date_joined__lte else None,
            'is_active': is_active_exact
        }

        arguments = {'profile__site': request._wagtail_site.pk}

        for key, value in filter_list.items():
            if value:
                arguments[key] = value
        self.send_export_email_to_celery(request.user.email, arguments)
        messages.success(request, _(
            "CSV emailed to '{0}'").format(request.user.email))
        return redirect(request.path)

    def get_template_names(self):
        return 'admin/frontend_users_admin_view.html'
