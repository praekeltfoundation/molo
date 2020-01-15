from django.test import TestCase
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguageRelation, Languages, Main


class TestEffectiveStyleHints(TestCase, MoloTestCaseMixin):

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
        self.new_section = self.mk_section(
            self.section_index,
            title="New Section",
            extra_style_hints='primary')

        self.new_section2 = self.mk_section(
            self.new_section, title="New Section 2")

        self.new_section3 = self.mk_section(
            self.section_index, title="New Section 3", slug="new-section-3")

        self.new_section4 = self.mk_section(
            self.new_section2, title="New Section 4", slug="new-section-4")

        self.new_section5 = self.mk_section(
            self.new_section,
            title="New Section 5", slug="new-section-5",
            extra_style_hints='secondary')

    def test_extra_css_set_on_current_section(self):
        self.assertEqual(
            self.new_section.get_effective_extra_style_hints(), 'primary')

    def test_extra_css_not_set_to_use_inherited_value(self):
        self.assertEqual(
            self.new_section2.get_effective_extra_style_hints(), 'primary')

    def test_extra_css_not_set_on_either_so_should_be_blank(self):
        self.assertEqual(
            self.new_section3.get_effective_extra_style_hints(), '')

        self.client.get('/locale/fr/')
        self.mk_section_translation(
            self.new_section3, self.french,
            title=self.new_section3.title + ' in french')

        response = self.client.get(
            '/sections-main-1/new-section-3-in-french/')
        self.assertContains(
            response,
            '<div class="section-listing section-listing--standard'
            ' section-listing--standard">')

        new_section6 = self.mk_section(
            self.new_section3,
            title="New Section 6", slug="new-section-6")

        self.mk_section_translation(
            new_section6, self.french, title=new_section6.title + ' in french')
        response = self.client.get(
            '/sections-main-1/new-section-3/new-section-6-in-french/')
        self.assertContains(
            response,
            '<div class="section-listing section-listing--standard'
            ' section-listing--standard">')

    def test_extra_css_not_set_on_child_so_should_use_parent_value(self):
        self.assertEqual(
            self.new_section4.get_effective_extra_style_hints(), 'primary')

    def test_extra_css_is_set_on_child_so_should_use_child_value(self):
        self.assertEqual(
            self.new_section5.get_effective_extra_style_hints(), 'secondary')

    def test_translated_page_so_should_use_main_lang_page_value(self):
        self.client.get('/locale/fr/')
        self.mk_section_translation(
            self.new_section4, self.french,
            title=self.new_section4.title + ' in french')

        response = self.client.get(
            '/sections-main-1/new-section/new-section-2/'
            'new-section-4-in-french/')
        self.assertContains(
            response,
            '<div class="section-listing section-listing--standard'
            ' section-listing--standardprimary">')

        new_section7 = self.mk_section(
            self.new_section3, title="New Section 7",
            slug="new-section-7", extra_style_hints='-en-hint')
        self.mk_section_translation(
            new_section7, self.french, title=new_section7.title + ' in french')
        response = self.client.get(
            '/sections-main-1/new-section-3/new-section-7-in-french/')
        self.assertContains(
            response,
            '<div class="section-listing section-listing--standard'
            ' section-listing--standard-en-hint">')

    def test_translated_page_so_should_use_translated_page_value(self):
        self.client.get('/locale/fr/')
        self.mk_section_translation(
            self.new_section5, self.french,
            title=self.new_section5.title + ' in french',
            extra_style_hints='-french-hint')
        response = self.client.get(
            '/sections-main-1/new-section/new-section-5-in-french/')
        self.assertContains(
            response,
            '<div class="section-listing section-listing--standard'
            ' section-listing--standard-french-hint">')
