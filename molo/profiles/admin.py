import unicodecsv as csv

from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import NotRegistered
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import localtime
from django.conf import settings
from django.db.models import Q

from daterange_filter.filter import DateRangeFilter
from wagtail.contrib.modeladmin.options import ModelAdmin as WagtailModelAdmin
from molo.profiles.admin_views import FrontendUsersAdminView
from molo.profiles.models import (
    UserProfile, SecurityQuestion, SecurityAnswer, SecurityQuestionIndexPage)

from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, DateWidget
from import_export.resources import ModelResource
from import_export.results import RowResult

from wagtail.wagtailcore.models import Site


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


def download_as_csv(ProfileUserAdmin, request, queryset):
    response = HttpResponse(content_type='text/csv', charset='utf-8')
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    writer = csv.writer(response, encoding='utf-8')
    user_model_fields = UserAdmin.list_display + ('date_joined', )
    profile_fields = ('alias', 'mobile_number')
    field_names = user_model_fields + profile_fields
    writer.writerow(field_names)
    for obj in queryset:
        obj.date_joined = obj.date_joined.strftime("%Y-%m-%d %H:%M")
        writer.writerow(
            [getattr(obj, field) for field in user_model_fields] +
            [getattr(obj.profile, field) for field in profile_fields])
    return response


download_as_csv.short_description = "Download selected as csv"


class UserProfileInlineModelAdmin(admin.StackedInline):
    model = UserProfile


class ProfileUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        'date_joined', '_alias', '_mobile_number', '_date_of_birth', '_gender')

    list_filter = UserAdmin.list_filter + ('date_joined', )

    actions = [download_as_csv]

    def _alias(self, obj, *args, **kwargs):
        if hasattr(obj, 'profile') and obj.profile.alias:
            return obj.profile.alias
        return ''

    def _mobile_number(self, obj, *args, **kwargs):
        if hasattr(obj, 'profile') and obj.profile.mobile_number:
            return obj.profile.mobile_number
        return ''

    def _date_of_birth(self, obj, *args, **kwargs):
        if hasattr(obj, 'profile') and obj.profile.date_of_birth:
            return obj.profile.date_of_birth
        return ''

    def _gender(self, obj, *args, **kwargs):
        if hasattr(obj, 'profile') and obj.profile.gender:
            return obj.profile.gender
        return ''

    def _site(self, obj, *args, **kwargs):
        if hasattr(obj, 'profile') and obj.profile.site:
            return obj.profile.site
        return ''


# Below here is for Wagtail Admin
class FrontendUsersDateRangeFilter(DateRangeFilter):
    template = 'admin/frontend_users_date_range_filter.html'


class CustomUsersListFilter(admin.SimpleListFilter):
    title = _('Type')
    parameter_name = 'usertype'

    def lookups(self, request, model_admin):
        return (
            ('frontend', _('Frontend Users')),
            ('admin', _('Admin Users')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'frontend':
            return queryset.filter(is_staff=False, groups__isnull=True)

        if self.value() == 'admin':
            return queryset.exclude(is_staff=False, groups__isnull=True)


class FrontendUsersModelAdmin(WagtailModelAdmin, ProfileUserAdmin):
    model = User
    menu_label = 'Users Export'
    menu_icon = 'user'
    menu_order = 600
    index_view_class = FrontendUsersAdminView
    add_to_settings_menu = True
    list_display = ('username', '_alias', '_mobile_number', '_date_of_birth',
                    'email', 'date_joined', 'is_active', '_site', '_gender')

    list_filter = (
        ('date_joined', FrontendUsersDateRangeFilter), 'is_active',
        CustomUsersListFilter)

    search_fields = ('username',)

    def get_queryset(self, request):
        return User.objects.filter(profile__site=request.site)


class UserProfileModelAdmin(WagtailModelAdmin, ProfileUserAdmin):
    model = UserProfile
    menu_label = 'Site Permissions'
    menu_icon = 'user'
    menu_order = 600
    index_view_class = FrontendUsersAdminView
    add_to_settings_menu = True
    list_display = ('user',)

    search_fields = ('user__username',)

    def get_queryset(self, request):
        return UserProfile.objects.all()


class TzDateTimeWidget(DateTimeWidget):

    def render(self, value, obj):
        if settings.USE_TZ:
            value = localtime(value)
        return super(TzDateTimeWidget, self).render(value, obj)


class MultiSiteUserResource(ModelResource):
    date_of_birth = Field(
        'profile__date_of_birth', 'date_of_birth', widget=DateWidget())
    alias = Field('profile__alias', 'alias')
    mobile_number = Field('profile__mobile_number', 'mobile_number')
    gender = Field('profile__gender', 'gender')
    migrated_username = Field(
        'profile__migrated_username', 'migrated_username')
    security_question_answers = Field(
        'profile__security_question_answers',
        'security_question_answers')
    date_joined = Field(
        'date_joined', 'date_joined', widget=TzDateTimeWidget())
    site = Field('profile__site__pk', 'site')

    class Meta:
        model = User
        exclude = ('id', 'is_superuser', 'groups',
                   'user_permissions', 'is_staff', 'last_login')
        export_order = ('username', 'first_name', 'last_name', 'email',
                        'is_active', 'date_joined', 'mobile_number',
                        'alias', 'date_of_birth', 'gender', 'site',
                        'migrated_username')
        import_id_fields = ['username']
        skip_unchanged = True

    def dehydrate_migrated_username(self, user):
        return user.username

    def dehydrate_security_question_answers(self, user):
        try:
            return [(x.question.title, x.answer)
                    for x in user.profile.securityanswer_set.all()]
        except:  # noqa
            return None

    def export(self, queryset=None, *args, **kwargs):
        qs = self._meta.model.objects.exclude(
            Q(is_staff=True) | Q(is_superuser=True))
        return super(MultiSiteUserResource, self).export(
            qs, *args, **kwargs)

    def get_prefixed_username(self, data):
        return '{}_{}'.format(data['site'], data['username']) \
            if data.get('site') else data['username']

    def before_import_row(self, row, **kwargs):
        row['username'] = self.get_prefixed_username(row)

    def import_row(self, row, instance_loader, *args, **kwargs):
        # Disable updating - we don't want to mistakenly override existing data
        if not User.objects.filter(
                username=self.get_prefixed_username(row)).exists():
            return super(MultiSiteUserResource, self).import_row(
                row, instance_loader, *args, **kwargs)

        row_result = self.get_row_result_class()()
        row_result.import_type = RowResult.IMPORT_TYPE_SKIP
        return row_result

    def import_field(self, field, obj, data):
        if field.attribute == 'profile__security_question_answers':
            site = Site.objects.get(pk=data.get('site'))
            security_index = SecurityQuestionIndexPage.objects.descendant_of(
                site.root_page).first()
            for x in data['security_question_answers']:
                # create the security question if it doesn't already exist
                sq = SecurityQuestion.objects.descendant_of(
                    security_index).filter(title=x[0])
                if not sq.exists():
                    sq = SecurityQuestion(title=x[0])
                    security_index.add_child(instance=sq)
                    sq.save_revision().publish()
                else:
                    sq = sq.first()

                # create the securty answer
                answer = SecurityAnswer(
                    question=sq, answer=x[1], user=obj.profile)
                # save separately so that we can pass in is_import
                answer.save(is_import=True)
        else:
            super(MultiSiteUserResource, self).import_field(field, obj, data)

    def import_obj(self, obj, data, dry_run):
        self.import_field(self.fields['username'], obj, data)
        obj.save()
        if data.get('site'):
            obj.profile.site = Site.objects.get(pk=data.get('site'))
            obj.profile.save()
        super(MultiSiteUserResource, self).import_obj(obj, data, dry_run)

    def after_save_instance(self, instance, using_transactions, dry_run):
        # Save related models
        instance.profile.save()


@admin.register(User)
class ProfilesUserAdmin(ImportExportModelAdmin, ProfileUserAdmin):
    resource_class = MultiSiteUserResource
    inlines = (UserProfileInlineModelAdmin, UserProfileInlineModelAdmin)
    list_display = ProfileUserAdmin.list_display
    actions = ProfileUserAdmin.actions
