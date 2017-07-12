# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_reaction_question_index(apps, schema_editor):
    from molo.core.models import ReactionQuestionIndexPage, Main
    main = Main.objects.all().first()

    if main:
        reaction_question_index = ReactionQuestionIndexPage(
            title='Reaction Questions', slug='reaction-questions')
        main.add_child(instance=reaction_question_index)
        reaction_question_index.save_revision().publish()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_reaction_questions'),
    ]

    operations = [
        migrations.RunPython(create_reaction_question_index),
    ]
