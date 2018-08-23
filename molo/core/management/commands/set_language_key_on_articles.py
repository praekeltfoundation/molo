from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from molo.core.models import LanguageRelation


class Command(BaseCommand):

    def handle(self, *args, **options):
        for relation in LanguageRelation.objects.all():
            if relation.page and relation.language:
                relation.page.language = relation.languages
                relation.page.save()
            else:
                self.stdout.write(self.style.NOTICE(
                    'Relation with pk "%s" is missing either page/language'
                    % (relation.pk)))
