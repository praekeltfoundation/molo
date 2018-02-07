from django.contrib.auth.models import User
from django.conf import settings
from celery import task
from django.core.mail import EmailMultiAlternatives
from molo.profiles.admin_import_export import FrontendUsersResource


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
    msg.send(fail_silently=False)
