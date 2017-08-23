import pytest

from elasticgit.tests.base import ModelBaseTest

from molo.core.models import SiteLanguageRelation, Main, Languages
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.api import Repo
from molo.core.content_import import api

from unicore.content import models as eg_models


@pytest.mark.django_db
class TestGetLanguages(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.mk_main()
        main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=main.get_site().pk)

        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='es',
            is_active=True)

        self.ws1 = self.create_workspace('1')
        self.ws2 = self.create_workspace('2')
        self.repo1 = Repo(self.ws1, 'repo1', 'Repo 1')
        self.repo2 = Repo(self.ws2, 'repo2', 'Repo 2')

    def test_get_locale(self):
        lang1 = eg_models.Localisation({'locale': 'eng_GB'})
        lang2 = eg_models.Localisation({'locale': 'spa_ES'})
        self.ws1.save(lang1, 'Added english')
        self.ws1.save(lang2, 'Added spanish')

        self.create_categories(self.ws1, locale='eng_GB', count=2)
        self.create_categories(self.ws1, locale='spa_ES', count=2)

        res = api.get_languages([self.repo1])

        self.assertEquals(res, {
            'locales': [{
                'locale': 'eng_GB',
                'name': 'English (United Kingdom)'
            }, {
                'locale': 'spa_ES',
                'name': 'Spanish (Spain)'
            }],
            'warnings': []
        })

    def test_get_locale_more_than_10(self):
        langs = [
            'eng_GB', 'spa_ES', 'spa_MX', 'por_PT', 'por_BR', 'hin_IN',
            'ind_ID', 'swa_TZ', 'swa_KE', 'afr_ZA', 'ara_AE', 'tha_TH']
        for l in langs:
            lang = eg_models.Localisation({'locale': l})
            self.ws1.save(lang, 'Added %s' % l)
            self.create_categories(self.ws1, locale='eng_GB', count=2)

        res = api.get_languages([self.repo1])

        self.assertEquals(len(res['locales']), 12)

    def test_get_locale_multirepo(self):
        lang1 = eg_models.Localisation({'locale': 'eng_GB'})
        lang2 = eg_models.Localisation({'locale': 'spa_ES'})
        self.ws1.save(lang1, 'Added english')
        self.ws1.save(lang2, 'Added spanish')
        self.ws2.save(lang1, 'Added english')
        self.ws2.save(lang2, 'Added spanish')

        self.create_categories(self.ws1, locale='eng_GB', count=2)
        self.create_categories(self.ws1, locale='spa_ES', count=2)
        self.create_categories(self.ws2, locale='eng_GB', count=2)
        self.create_categories(self.ws2, locale='spa_ES', count=2)

        res = api.get_languages([self.repo1, self.repo2])

        self.assertEquals(res, {
            'locales': [{
                'locale': 'eng_GB',
                'name': 'English (United Kingdom)'
            }, {
                'locale': 'spa_ES',
                'name': 'Spanish (Spain)'
            }],
            'warnings': []
        })

    def test_get_locale_multirepo_strays(self):
        lang1 = eg_models.Localisation({'locale': 'eng_GB'})
        lang2 = eg_models.Localisation({'locale': 'spa_ES'})
        lang3 = eg_models.Localisation({'locale': 'spa_MX'})
        lang4 = eg_models.Localisation({'locale': 'spa_CU'})

        self.ws1.save(lang1, 'Added english')
        self.ws1.save(lang2, 'Added spanish es')
        self.ws1.save(lang3, 'Added spanish mx')

        self.ws2.save(lang2, 'Added spanish es')
        self.ws2.save(lang3, 'Added spanish mx')
        self.ws2.save(lang4, 'Added spanish cu')

        self.create_categories(self.ws1, locale='eng_GB', count=2)
        self.create_categories(self.ws1, locale='spa_ES', count=2)
        self.create_categories(self.ws1, locale='spa_MX', count=2)

        self.create_categories(self.ws2, locale='spa_ES', count=2)
        self.create_categories(self.ws2, locale='spa_MX', count=2)
        self.create_categories(self.ws2, locale='spa_CU', count=2)

        res = api.get_languages([self.repo1, self.repo2])

        self.assertEquals(res, {
            'locales': [{
                'locale': 'eng_GB',
                'name': 'English (United Kingdom)'
            }, {
                'locale': 'spa_CU',
                'name': 'Spanish (Cuba)'
            }, {
                'locale': 'spa_ES',
                'name': 'Spanish (Spain)'
            }, {
                'locale': 'spa_MX',
                'name': 'Spanish (Mexico)'
            }],
            'warnings': [{
                'type': 'stray_locale',
                'details': {
                    'repo': 'repo1',
                    'locale': 'eng_GB',
                    'name': 'English (United Kingdom)'
                }
            }, {
                'type': 'stray_locale',
                'details': {
                    'repo': 'repo2',
                    'locale': 'spa_CU',
                    'name': 'Spanish (Cuba)'
                }
            }]
        })

    def test_unknown_locale(self):
        lang1 = eg_models.Localisation({'locale': 'eng_GB'})
        lang2 = eg_models.Localisation({'locale': 'Zre_ZR'})

        self.ws1.save(lang1, 'Added english language')
        self.ws1.save(lang2, 'Added a language with unknown locale')

        self.create_categories(self.ws1, locale='eng_GB', count=2)
        self.create_categories(self.ws1, locale='Zre_ZR', count=2)

        res = api.get_languages([self.repo1])

        self.assertEquals(res, {
            'locales': [
                {'locale': u'Zre_ZR', 'name': u'Zre_ZR'},
                {'locale': 'eng_GB', 'name': 'English (United Kingdom)'}
            ],
            'warnings': []
        })
