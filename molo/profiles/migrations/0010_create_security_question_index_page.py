from __future__ import unicode_literals

from django.db import migrations, models


def create_section_index(apps, schema_editor):
    from molo.core.models import Main
    from molo.profiles.models import SecurityQuestionIndexPage
    main = Main.objects.all().first()
    index_page = SecurityQuestionIndexPage.objects.filter(
        slug='security-questions').first()

    if main and not index_page:
        index_page = SecurityQuestionIndexPage(
            title='Security Questions', slug='security-questions')
        main.add_child(instance=index_page)
        index_page.save_revision().publish()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_add_security_question_index_page'),
    ]

    operations = [
        migrations.RunPython(create_section_index),
    ]
