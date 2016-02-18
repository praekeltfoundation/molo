import pytest

from django.test import TestCase
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguage, SectionPage
from django.core.urlresolvers import reverse


@pytest.mark.django_db
class TestTranslations(TestCase, MoloTestCaseMixin):
    def setUp(self):
        # Creates Main language
        self.english = SiteLanguage.objects.create(
            title='english', code='en'
        )
        # Creates translation Language
        self.french = SiteLanguage.objects.create(
            title='french', code='fr'
        )

        # Creates main page
        self.mk_main()
        # Creates a section under the main page
        self.english_section = self.mk_section(
            self.main, title='English section')
        # Creates a sub-section under the section
        self.english_subsection = self.mk_section(
            self.english_section, title='English subsection')

        # Login
        self.user = self.login()

    def test_wagtail_main_page(self):
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.main.id]))
        self.assertContains(response, 'English section')

    def test_wagtail_root_page_has_no_translations(self):
        response = self.client.get(reverse(
            'wagtailadmin_explore_root'))
        self.assertNotContains(response, 'french')

    def test_that_all_translation_languages_are_listed(self):
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.main.id]))
        # Checks main language is not listed as translation language
        self.assertNotContains(response, 'title="english">english')
        # Checks if translation language exists
        self.assertContains(response, 'title="french">french')

    def test_that_only_main_language_pages_are_listed(self):
        self.client.post(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.main.id]))
        # checks that only the english section is listed
        # and not the french section
        self.assertContains(response, 'English section')
        self.assertNotContains(response,
                               'french translation of English section')

    def test_page_doesnt_have_translation_action_button_links_to_addview(self):
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.main.id]))
        self.assertContains(response,
                            '<a href="/admin/translations/add/%s/fr/"'
                            % self.english_section.id)

    def test_that_translation_have_the_right_language(self):
        self.client.get(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        page = SectionPage.objects.get(
            slug='french-translation-of-english-section')
        self.assertEquals(page.languages.all()[0].language.title, 'french')

    def test_draft_translations_have_additional_css_clsss(self):
        self.client.post(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        page = SectionPage.objects.get(
            slug='french-translation-of-english-section')

        # Ckecks when the translated page is draf
        # the translation button has the right css
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.main.id]))
        self.assertContains(
            response, 'class="button button-small button-secondary '
            'translation-translated translation-translated-draft" '
            'title="french">french</a>')

        # Ckecks when the translated page is Draft + live
        # the translation button has the right css
        page.save_revision().publish()
        page.save_revision()
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.main.id]))
        self.assertContains(
            response, 'class="button button-small button-secondary '
            'translation-translated translation-translated-draft" '
            'title="french">french</a>')
        # Ckecks when the translated page is Publish
        # the translation button has the right css
        page.save_revision().publish()
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.main.id]))

        self.assertContains(
            response, 'class="button button-small button-secondary '
            'translation-translated " title="french">french</a>')

    def test_if_page_has_a_translation_the_action_links_to_the_edit_page(self):
        self.client.post(reverse(
            'add_translation', args=[self.english_section.id, 'fr']))
        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.main.id]))
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
            'wagtailadmin_explore', args=[self.main.id]))
        self.assertContains(
            response, 'class="button button-small button-secondary '
            'translation-translated " title="french">french</a>')

        self.client.post(reverse(
            'wagtailadmin_pages:unpublish', args=[self.english_section.id]))

        self.english_section = SectionPage.objects.get(
            id=self.english_section.id)

        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.main.id]))
        self.assertContains(
            response, 'class="button button-small button-secondary '
            'translation-translated " title="french">french</a>')

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
            'add_translation', args=[self.main.id, 'fr']))
        self.assertRedirects(response, reverse('wagtailadmin_home'))
