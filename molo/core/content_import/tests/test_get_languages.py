import pytest

from elasticgit.tests.base import ModelBaseTest

from molo.core.models import SiteLanguage
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.api import Repo
from molo.core.content_import import api

from unicore.content import models as eg_models


@pytest.mark.django_db
class TestGetLanguages(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.english = SiteLanguage.objects.create(
            locale='en',
        )
        self.spanish = SiteLanguage.objects.create(
            locale='es',
        )
        self.mk_main()

        self.repo1 = Repo('repo1', self.create_workspace())
        self.ws1 = self.repo1.workspace

    def test_unknown_locale(self):
        lang1 = eg_models.Localisation({'locale': 'eng_GB'})
        lang2 = eg_models.Localisation({'locale': 'Zre_ZR'})

        self.ws1.save(lang1, 'Added english language')
        self.ws1.save(lang2, 'Added a language with unknown locale')

        [cat_eng_1, cat_eng_2] = self.create_categories(
            self.ws1, locale='eng_GB', count=2)
        [cat_Zre_1, cat_Zre_2] = self.create_categories(
            self.ws1, locale='Zre_ZR', count=2)

        locales, errors = api.get_languages([self.repo1])
        self.assertEquals(errors, [
            {'type': 'unknown_locale', 'details': {'locale': u'Zre_ZR'}}])
