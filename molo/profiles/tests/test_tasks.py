# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.conf import settings
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import Main, Languages, SiteLanguageRelation
from molo.profiles.task import send_export_email
from django.urls import reverse


class ModelsTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'testing1',
            'password': '1234',
            'terms_and_conditions': True

        })
        client = Client(HTTP_HOST=self.site2.hostname)
        client.post('/profiles/register/', {
            'username': 'testing2',
            'password': '1234',
            'terms_and_conditions': True

        })
        self.user = User.objects.get(username='testing1')
        self.user2 = User.objects.get(username='testing2')
        profile = self.user.profile
        profile.alias = 'The Alias'
        profile.mobile_number = '+27784667723'
        profile.site = Main.objects.all().first().get_site()
        profile.save()
        self.field_names = (
            'username', 'first_name', 'last_name',
            'email', 'is_active', 'date_joined', 'last_login')
        self.profile_field_names = (
            'alias', 'date_of_birth', 'mobile_number'
        )

    def test_send_export_email(self):
        send_export_email('examplemail@test.com', {'profile__site': self.site})
        message = list(mail.outbox)[0]
        self.assertEqual(message.to, ['examplemail@test.com'])
        self.assertEqual(
            message.subject, 'Molo export: ' + settings.SITE_NAME)
        self.assertEqual(
            message.attachments[0],
            ('Molo_export_testapp.csv',
             'username,alias,first_name,last_name,date_of_birth,email,mobile_n'
             'umber,is_active,date_joined,last_login,gender,'
             'uuid\r\ntesting1,The '
             'Alias,,,,,+27784667723,1,' + str(
                 self.user.date_joined.strftime("%Y-%m-%d %H:%M:%S")) +
             ',' + str(
                 self.user.last_login.strftime("%Y-%m-%d %H:%M:%S")) +
             ',,' + str(
                 self.user.profile.uuid) + '\r\n',
             'text/csv'))

        # test sending from the second site
        send_export_email(
            'examplemail@test.com', {'profile__site': self.site2})
        message = list(mail.outbox)[1]
        self.assertEqual(
            message.attachments[0],
            ('Molo_export_testapp.csv',
             'username,alias,first_name,last_name,date_of_birth,email,mobile_n'
             'umber,is_active,date_joined,last_login,gender,uuid\r\ntesting2'
             ',,,,,,,1,' + str(
                    self.user2.date_joined.strftime("%Y-%m-%d %H:%M:%S")) +
             ',' + str(
                 self.user2.last_login.strftime("%Y-%m-%d %H:%M:%S")) +
             ',,' + str(
                 self.user2.profile.uuid) + '\r\n', 'text/csv'))
