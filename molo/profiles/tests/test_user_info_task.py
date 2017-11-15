from datetime import datetime, timedelta
import random
from itertools import izip
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles import task
import responses
import json


class UserInfoTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        '''
        populates the database with 20 users with the following properties:
        10 users that joined in the last 24 hours
        7 users
            who joined longer than 24 hours ago
            and visited the site in the last 24 hours
        3 users
            who joined longer than 24 hours ago
            and have not visited the site in the last 24 hours
        '''
        self.mk_main()
        now = datetime.now()

        # create users that joined today
        for x in range(10):
            join_datetime = now - timedelta(hours=random.randint(1, 23))
            user = User.objects.create_user(
                username='tester' + str(x),
                email='tester' + str(x) + '@example.com',
                password='tester')
            user.date_joined = join_datetime
            user.last_login = join_datetime
            user.save()

        join_datetimes = []
        login_datetimes = []

        # create 10 datetimes not within the previous 24 hours
        for x in range(10):
            join_datetimes.append(now -
                                  timedelta(days=random.randint(1, 1000)))

        # create 7 datetimes that are within that past 24 hours
        for x in range(7):
            login_datetimes.append(now -
                                   timedelta(hours=random.randint(1, 23)))

        # create last login that's after the joined date
        # but before 24 hours before today
        for x in range(3):
            temp_datetime = 0
            while(True):
                temp_datetime = (now - timedelta(days=random.randint(1, 1000)))

                if((temp_datetime < (now - timedelta(hours=24)))and
                   (temp_datetime > join_datetimes[7 + x])):
                    break
            login_datetimes.append(temp_datetime)

        # create the users
        count = 10
        for join_datetime, login_datetime in izip(join_datetimes,
                                                  login_datetimes):
            user = User.objects.create_user(
                username='tester' + str(count),
                email='tester' + str(count) + '@example.com',
                password='tester')
            user.date_joined = join_datetime
            user.last_login = login_datetime
            user.save()
            count += 1

    # setup response

    responses.add(
        responses.POST,
        'http://testserver:8080/',
        status=200, content_type='application/json',
        body=json.dumps({}))

    def test_new_user_count(self):
        self.assertEqual(task.get_count_of_new_users(), 10)

    def test_returning_user_count(self):
        self.assertEqual(task.get_count_of_returning_users(), 7)

    def test_total_user_count(self):
        self.assertEqual(task.get_count_of_all_users(), 20)

    def test_user_info_message(self):
        self.assertEqual(task.get_message_text(),
                         ("DAILY UPDATE ON USER DATA\n"
                          "New User - joined in the last 24 hours\n"
                          "Returning User - joined longer than 24 hours ago"
                          "and visited the site in the last 24 hours\n"
                          "```"
                          "Total Users: 20\n"
                          "New Users: 10\n"
                          "Returning Users: 7"
                          "```"))

    @responses.activate
    @override_settings(SLACK_INCOMING_WEBHOOK_URL="http://testserver:8080/")
    def test_send_user_data_to_slack(self):
        task.send_user_data_to_slack()
