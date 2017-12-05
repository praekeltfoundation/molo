from django.shortcuts import render
from molo.profiles.admin import FrontendUsersModelAdmin, UserProfileModelAdmin
from molo.profiles.models import (
    UserProfilesSettings, UserProfile, SecurityAnswer)
from wagtail.contrib.modeladmin.options import modeladmin_register
from wagtail.wagtailadmin.site_summary import SummaryItem
from wagtail.wagtailcore import hooks


class ProfileWarningMessagee(SummaryItem):
    order = 100
    template = 'admin/profile_warning_message.html'


@hooks.register('construct_homepage_panels')
def profile_warning_message(request, panels):
    profile_settings = UserProfilesSettings.for_site(request.site)
    if not profile_settings.country_code and \
            profile_settings.show_mobile_number_field:
        panels[:] = [ProfileWarningMessagee(request)]


modeladmin_register(FrontendUsersModelAdmin)
modeladmin_register(UserProfileModelAdmin)


class AccessErrorMessage(SummaryItem):
    order = 100
    template = 'wagtail/access_error_message.html'


@hooks.register('construct_homepage_panels')
def add_access_error_message_panel(request, panels):
    if UserProfile.objects.filter(user=request.user).exists() and \
            not request.user.is_superuser:
        if not request.user.profile.admin_sites.filter(
                pk=request.site.pk).exists():
            panels[:] = [AccessErrorMessage(request)]


@hooks.register('before_delete_page')
def before_delete_security_question(request, page):
    if SecurityAnswer.objects.filter(question_id=page.id):
        return render(
            request, 'admin/security_question_delete_warrning.html', {
                'page': page,
                'parent_id': page.get_parent().id
            })
