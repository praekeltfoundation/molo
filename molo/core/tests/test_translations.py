import pytest

from datetime import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase

from wagtail.wagtailcore.models import Site

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SectionPage, SiteSettings, \
    ArticlePage, Main, SiteLanguageRelation, Languages, ArticlePageTags
from molo.core.tasks import promote_articles


@pytest.mark.django_db
class TestTranslations(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='fr',
            is_active=True)
        self.spanish_mexico = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='es-mx',
            is_active=True)

        # Creates a section under the main page
        self.english_section = self.mk_section(
            self.section_index, title='English section')
        # Creates a sub-section under the section
        self.english_subsection = self.mk_section(
            self.english_section, title='English subsection')

        # Login
        self.user = self.login()

    def test_section_index_page(self):
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.section_index.id]))
        self.assertContains(response, 'English section')

    def test_wagtail_root_page_has_no_translations(self):
        response = self.client.get(reverse(
            'wagtailadmin_explore_root'))
        self.assertNotContains(response, 'French')

    def test_that_all_translation_languages_are_listed(self):
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.section_index.id]))
        # Checks main language is not listed as translation language
        self.assertNotContains(response, 'title="English">English')
        # Checks if translation language exists
        self.assertContains(response, 'title="French">French')
        self.assertContains(response,
                            'title="Mexican Spanish">Mexican Spanish')

    def test_that_only_main_language_pages_are_listed(self):
        self.client.post(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.section_index.id]))
        # checks that only the english section is listed
        # and not the french section
        self.assertContains(response, 'English section')
        self.assertNotContains(response,
                               'French translation of English section')

    def test_page_doesnt_have_translation_action_button_links_to_addview(self):
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.section_index.id]))
        self.assertContains(response,
                            '<a href="/admin/translations/add/%s/fr/"'
                            % self.english_section.id)

    def test_that_translation_have_the_right_language(self):
        self.client.get(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        page = SectionPage.objects.get(
            slug='french-translation-of-english-section')
        self.assertEquals(str(page.languages.all()[0].language), 'French')

    def test_draft_translations_have_additional_css_clsss(self):
        self.client.post(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        page = SectionPage.objects.get(
            slug='french-translation-of-english-section')

        # Ckecks when the translated page is draf
        # the translation button has the right css
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.section_index.id]))
        self.assertContains(
            response, 'class="button button-small button-secondary '
            'translation-translated translation-translated-draft" '
            'title="French">French</a>')

        # Ckecks when the translated page is Draft + live
        # the translation button has the right css
        page.save_revision().publish()
        page.save_revision()
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.section_index.id]))
        self.assertContains(
            response, 'class="button button-small button-secondary '
            'translation-translated translation-translated-draft" '
            'title="French">French</a>')
        # Ckecks when the translated page is Publish
        # the translation button has the right css
        page.save_revision().publish()
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.section_index.id]))

        self.assertContains(
            response, 'class="button button-small button-secondary '
            'translation-translated " title="French">French</a>')

    def test_if_page_has_a_translation_the_action_links_to_the_edit_page(self):
        self.client.post(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.section_index.id]))
        page = SectionPage.objects.get(
            slug='french-translation-of-english-section')
        self.assertContains(response,
                            '<a href="/admin/pages/%s/edit/"'
                            % page.id)

    def test_republishing_main_section_effecting_translated_section(self):
        self.client.post(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        page = SectionPage.objects.get(
            slug='french-translation-of-english-section')
        page.save_revision().publish()
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.section_index.id]))
        self.assertContains(
            response, 'class="button button-small button-secondary '
            'translation-translated " title="French">French</a>')

        self.client.post(reverse(
            'wagtailadmin_pages:unpublish', args=[self.english_section.id]))

        self.english_section = SectionPage.objects.get(
            id=self.english_section.id)

        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.section_index.id]))
        self.assertContains(
            response, 'class="button button-small button-secondary '
            'translation-translated " title="French">French</a>')

    def test_adding_translation_that_already_exists_redirects_to_edit(self):
        self.client.post(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))

        response = self.client.post(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        page = SectionPage.objects.get(
            slug='french-translation-of-english-section')
        self.assertRedirects(
            response, reverse('wagtailadmin_pages:edit', args=[page.id]))

    def test_adding_translation_to_non_translatable_page_redirects_home(self):
        response = self.client.post(reverse(
            'add_translation', args=[self.section_index.id, 'fr']))
        self.assertRedirects(response, reverse('wagtailadmin_home'))

    def test_site_languages_summary(self):
        self.client.post(reverse(
            'add_translation', args=[self.english_subsection.id, 'fr']))
        self.client.post(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        page = SectionPage.objects.get(
            slug='french-translation-of-english-section')
        page.save_revision().publish()
        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertContains(response, '<span>2</span>English Pages')
        self.assertContains(response, '<span>2</span>French Pages')

    def test_site_exists_if_no_iems_translated_for_translated_only(self):
        site_settings = SiteSettings.for_site(self.main.get_site())
        site_settings.enable_tag_navigation = True
        site_settings.show_only_translated_pages = True
        site_settings.save()

        tag = self.mk_tag(parent=self.tag_index)
        tag.feature_in_homepage = True
        tag.save_revision().publish()
        articles = self.mk_articles(
            parent=self.english_section,
            featured_in_latest_start_date=datetime.now(),
            featured_in_homepage_start_date=datetime.now(), count=30)
        for article in articles:
            ArticlePageTags.objects.create(page=article, tag=tag)

        promote_articles()

        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/locale/fr/')
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_that_only_translated_sections_show_with_tag_navigation(self):
        site_settings = SiteSettings.for_site(self.main.get_site())
        site_settings.enable_tag_navigation = True
        site_settings.show_only_translated_pages = True
        site_settings.save()

        self.mk_section_translation(
            self.english_section, self.french,
            title=self.english_section.title + ' in french')

        article1 = self.mk_article(
            self.english_section,
            title='English article1 in English Section',
            featured_in_homepage_start_date=datetime.now(),
            featured_in_homepage=True)
        self.mk_article_translation(
            article1, self.french, title=article1.title + ' in french',)

        promote_articles()

        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/"'
            ' class="section-listing__theme-bg-link">English section</a>')
        response = self.client.get('/locale/fr/')
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section-in-french/"'
            ' class="section-listing__theme-bg-link">'
            'English section in french</a>')

    def test_that_only_translated_pages_are_shown_on_front_end(self):
        # set the site settings show_only_translated_pages to True
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        setting.show_only_translated_pages = True
        setting.save()

        eng_section2 = self.mk_section(
            self.section_index, title='English section2')
        self.mk_section_translation(
            eng_section2, self.french,
            title=eng_section2.title + ' in french')

        article1 = self.mk_article(
            eng_section2,
            title='English article1 in section 2',
            featured_in_latest_start_date=datetime.now(),
            featured_in_homepage_start_date=datetime.now())
        self.mk_article_translation(
            article1, self.french, title=article1.title + ' in french',)

        article2 = self.mk_article(
            self.english_section,
            title='English article2 in section 1',
            featured_in_latest_start_date=datetime.now(),
            featured_in_homepage_start_date=datetime.now())
        self.mk_article_translation(
            article2, self.french, title=article2.title + ' in french',)
        promote_articles()

        # tests that in Home page users will only see the sections
        # that have been translated
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/"'
            ' class="section-listing__theme-bg-link">English section</a>')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section2/"'
            ' class="section-listing__theme-bg-link">English section2</a>')
        response = self.client.get('/locale/fr/')
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section2-in-french/"'
            ' class="section-listing__theme-bg-link">'
            'English section2 in french</a>')
        self.assertNotContains(
            response,
            '<a href="/sections-main-1/english-section/"'
            ' class="section-listing__theme-bg-link">English section</a>')

        en_page = self.mk_article(self.english_section,
                                  title='English article1',
                                  featured_in_latest_start_date=datetime.now())
        promote_articles()
        en_page = ArticlePage.objects.get(title=en_page.title)
        self.mk_article_translation(
            en_page, self.french, title=en_page.title + ' in french',)

        self.mk_article(self.english_section,
                        title='English article2',
                        featured_in_latest_start_date=datetime.now())
        promote_articles()

        # tests that in english section users will only see the articles
        # that have been translated
        response = self.client.get('/locale/en/')
        response = self.client.get('/sections-main-1/english-section/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/english-article1-3/" '
            'class="promoted-article-list__anchor">'
            '<h3 class="heading promoted-article__title">'
            'English article1'
            '</h3></a>', html=True)
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/english-article2-2/" '
            'class="promoted-article-list__anchor">'
            '<h3 class="heading promoted-article__title">'
            'English article2'
            '</h3></a>', html=True)

        response = self.client.get('/locale/fr/')
        response = self.client.get('/sections-main-1/english-section/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/'
            'english-article1-in-french/" '
            'class="promoted-article-list__anchor">'
            '<h3 class="heading promoted-article__title">'
            'English article1 in french'
            '</h3></a>', html=True)
        self.assertNotContains(
            response,
            '<a href="/sections-main-1/english-section/english-article2-2/" '
            'class="promoted-article-list__anchor">'
            '<h3 class="heading promoted-article__title">'
            'English article2'
            '</h3></a>', html=True)

        # tests that in latest block users will only see the articles
        # that have been translated
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/'
            'english-article1-in-french/" '
            'class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-headings">'
            '<h5 class="heading'
            ' promoted-article__title--theme-headings">'
            'English article1 in french'
            '</h5></a>', html=True)
        self.assertNotContains(
            response,
            '<a href="/sections-main-1/english-section/'
            'english-article1-3/" '
            'class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-headings">'
            '<h5 class="heading'
            ' promoted-article__title--theme-headings">'
            'English article1'
            '</h5></a>', html=True)

        response = self.client.get('/locale/en/')
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/english-article1-3/"'
            ' class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-headings">'
            '<h5 class="heading'
            ' promoted-article__title--theme-headings">English article1</h5>'
            '</a>', html=True)
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/english-article2-2/"'
            ' class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-headings">'
            '<h5 class="heading'
            ' promoted-article__title--theme-headings">English article2</h5>'
            '</a>', html=True)

    def test_if_main_lang_page_unpublished_translated_page_still_shows(self):
        eng_section2 = self.mk_section(
            self.section_index, title='English section2')
        self.mk_section_translation(
            eng_section2, self.french,
            title=eng_section2.title + ' in french')
        eng_section2.unpublish()

        self.mk_article(
            eng_section2,
            title='English article1 in section 2',
            featured_in_latest_start_date=datetime.now(),
            featured_in_homepage_start_date=datetime.now())

        en_page = self.mk_article(
            self.english_section,
            title='English article1',
            featured_in_latest_start_date=datetime.now(),
            featured_in_homepage_start_date=datetime.now())
        promote_articles()
        self.mk_article_translation(
            en_page, self.french, title=en_page.title + ' in french',)

        en_page2 = self.mk_article(
            self.english_section,
            title='English article2',
            featured_in_latest_start_date=datetime.now())
        promote_articles()
        en_page2 = ArticlePage.objects.get(title=en_page2.title)
        self.mk_article_translation(
            en_page2, self.french, title=en_page2.title + ' in french',)
        en_page2.unpublish()

        # tests that on home page users will only
        # see the pages that are published
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/"'
            ' class="section-listing__theme-bg-link">English section</a>')
        self.assertNotContains(
            response,
            '<a href="/sections-main-1/english-section2/"'
            ' class="section-listing__theme-bg-link">English section2</a>')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/english-article1-3/"'
            ' class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-bg">'
            '<h3 class="heading '
            'promoted-article-list__heading">'
            ' English article1</h3></a>',
            html=True)

        self.assertNotContains(
            response,
            '<a href="/sections-main-1/english-section/english-article2-3/"'
            ' class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-bg">'
            '<h3 class="heading'
            ' promoted-article-list__heading">'
            ' English article2</h3></a>',
            html=True)

        response = self.client.get('/sections-main-1/english-section/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/english-article1-3/"'
            ' class="promoted-article-list__anchor">'
            '<h3 class="heading promoted-article__title">'
            'English article1</h3></a>', html=True)
        self.assertNotContains(
            response,
            '<a href="/sections-main-1/english-section/english-article2/"'
            ' class="promoted-article-list__anchor">'
            '<h3 class="heading promoted-article__title">'
            'English article2</h3></a>', html=True)

        # tests that when switching to a child language
        # users will see all the published translated pages
        # even if the main language page is unpublished

        response = self.client.get('/locale/fr/')
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/"'
            ' class="section-listing__theme-bg-link">English section</a>')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section2-in-french/"'
            ' class="section-listing__theme-bg-link">'
            'English section2 in french</a>')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/'
            'english-article1-in-french/"'
            ' class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-bg">'
            '<h3 class="heading'
            ' promoted-article-list__heading">'
            'English article1 in french</h3>', html=True)
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section2/'
            'english-article1-in-section-2/" '
            'class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-bg">'
            '<h3 class="heading'
            ' promoted-article-list__heading">'
            'English article1 in section 2</h3></a>',
            html=True)

        response = self.client.get('/sections-main-1/english-section/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/'
            'english-article1-in-french/"'
            ' class="promoted-article-list__anchor">'
            '<h3 class="heading'
            ' promoted-article__title">English article1 in french</h3></a>',
            html=True)
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section/'
            'english-article2-in-french/"'
            ' class="promoted-article-list__anchor">'
            '<h3 class="heading'
            ' promoted-article__title">English article2 in french</h3></a>',
            html=True)

    def test_if_mexican_spanish_translated_pages_are_shown_on_front_end(self):
        en_section2 = self.mk_section(
            self.section_index, title='English section2')
        self.mk_section_translation(
            en_section2, self.spanish_mexico,
            title=en_section2.title + ' in Mexican Spanish')

        en_page = self.mk_article(
            en_section2,
            title='English article1',
            featured_in_latest_start_date=datetime.now(),
            featured_in_homepage_start_date=datetime.now())
        promote_articles()
        self.mk_article_translation(
            en_page, self.spanish_mexico,
            title=en_page.title + ' in Mexican Spanish',)

        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section2/"'
            ' class="section-listing__theme-bg-link">English section2</a>')
        self.assertNotContains(
            response,
            'English section2 in Mexican Spanish')

        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section2/english-article1/" '
            'class="promoted-article-list__anchor '
            'promoted-article-list__anchor--theme-bg">'
            '<h3 class="heading'
            ' promoted-article-list__heading">'
            'English article1</h3></a>', html=True)
        self.assertNotContains(
            response,
            'English article1 in Mexican Spanish')

        response = self.client.get('/locale/es-mx/')
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section2-in-mexican-spanish/"'
            ' class="section-listing__theme-bg-link">'
            'English section2 in Mexican Spanish</a>')
        self.assertContains(
            response,
            '<a href="/sections-main-1/english-section2/'
            'english-article1-in-mexican-spanish/"'
            ' class="promoted-article-list__anchor '
            'promoted-article-list__anchor--theme-bg">'
            '<h3 class="heading'
            ' promoted-article-list__heading">'
            'English article1 in Mexican Spanish</h3></a>', html=True)
