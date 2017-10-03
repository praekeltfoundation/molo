# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import Main, Languages, SiteLanguageRelation


class PermissionsTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.mk_main2()
        self.client = Client()

        self.wagtail_login_only_group, _created = Group.objects.get_or_create(
            name='Wagtail Login Only')

        wagtailadmin_content_type, created = ContentType.objects.get_or_create(
            app_label='wagtailadmin',
            model='admin'
        )

        # Create admin permission
        admin_permission, created = Permission.objects.get_or_create(
            content_type=wagtailadmin_content_type,
            codename='access_admin',
            name='Can access Wagtail admin'
        )

        # add the wagtail login permissions to group
        access_admin = Permission.objects.get(codename='access_admin')
        self.wagtail_login_only_group.permissions.add(access_admin)

        self.admin_user = User.objects.create_user(
            username='username', password='password', email='login@email.com')
        self.admin_user.groups.add(self.wagtail_login_only_group)

    def test_staff_user_unable_to_log_in_main_without_permission(self):
        # it should not allow you to log into site one
        self.client.login(username='username', password='password')
        response = self.client.get('/admin/')
        self.assertContains(response, 'You do not have access to this site.')

        # it should not show any pages for users with no access
        self.assertTrue(self.main.get_descendants().count() > 0)
        response = self.client.get('/admin/pages/%s/' % self.main.pk)
        self.assertContains(
            response, 'No pages have been created at this location')

        self.admin_user.profile.admin_sites.add(self.site)
        response = self.client.get('/admin/')
        self.assertNotContains(
            response, 'You do not have access to this site.')
        # once admin has access it should show the pages
        response = self.client.get('/admin/pages/%s/' % self.main.pk)
        self.assertNotContains(
            response, 'No pages have been created at this location')
