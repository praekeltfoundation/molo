import requests
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.conf import settings
from celery import task
from django.core.mail import EmailMultiAlternatives
from molo.profiles.admin_import_export import FrontendUsersResource


def get_count_of_new_users():
    now = datetime.now()
    qs = User.objects.filter(date_joined__gte=now - timedelta(hours=24))
    return qs.count()


def get_count_of_returning_users():
    now = datetime.now()
    qs = User.objects.filter(last_login__gte=now - timedelta(hours=24)).filter(
        date_joined__lt=now - timedelta(hours=24))
    return qs.count()


def get_count_of_all_users():
    qs = User.objects.all()
    return qs.count()


def get_message_text():
    return ("DAILY UPDATE ON USER DATA\n"
            "New User - joined in the last 24 hours\n"
            "Returning User - joined longer than 24 hours ago"
            "and visited the site in the last 24 hours\n"
            "```"
            "Total Users: {0}\n"
            "New Users: {1}\n"
            "Returning Users: {2}"
            "```"
            .format(get_count_of_all_users(),
                    get_count_of_new_users(),
                    get_count_of_returning_users()))


@task(serializer='json')
def send_user_data_to_slack():
    try:
        url = settings.SLACK_INCOMING_WEBHOOK_URL
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        data = {
            "text": get_message_text()
        }
        requests.post(url, json=data, headers=headers)
    except AttributeError:
        pass


@task(ignore_result=True)
def send_export_email(recipient, arguments):
    csvfile = FrontendUsersResource().export(
        User.objects.filter(is_staff=False, **arguments)).csv
    subject = 'Molo export: %s' % settings.SITE_NAME
    from_email = settings.DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(subject, '', from_email, (recipient,))
    msg.attach(
        'Molo_export_%s.csv' % settings.SITE_NAME,
        csvfile, 'text/csv')
    msg.send()
