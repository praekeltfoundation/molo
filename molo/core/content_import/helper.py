import json

from babel import Locale

from molo.core.models import (
    Main, SiteLanguage, PageTranslation, SectionPage, ArticlePage, FooterPage)
from molo.core.content_import.get_image import get_image_file

from unicore.content.models import Category, Page


class ContentImportHelper(object):

    def __init__(self, ws):
        self.ws = ws

    def get_or_create(self, cls, obj, parent):
        if cls.objects.filter(uuid=obj.uuid).exists():
            return cls.objects.get(uuid=obj.uuid)

        instance = cls(uuid=obj.uuid, title=obj.title)
        parent.add_child(instance=instance)
        print 'created', obj.title
        return instance

    def get_or_create_translation(self, cls, obj, parent, language):
        if cls.objects.filter(uuid=obj.uuid).exists():
            return cls.objects.get(uuid=obj.uuid)

        instance = cls(uuid=obj.uuid, title=obj.title)
        parent.add_child(instance=instance)
        language_relation = instance.languages.first()
        language_relation.language = language
        language_relation.save()
        print 'created translation', obj.title
        return instance

    def import_section_content(self, c, site_language):
        main = Main.objects.all().first()
        if site_language.is_main_language:
            section = self.get_or_create(SectionPage, c, main)
        else:
            section = self.get_or_create_translation(
                SectionPage, c, main, site_language)

        section.description = c.subtitle
        if c.image_host and c.image:
            section.image = get_image_file(c.image_host, c.image)

        section.save_revision().publish()

        return section

    def import_page_content(self, p, site_language):
        if site_language.is_main_language:
            if p.primary_category:
                try:
                    section = SectionPage.objects.get(
                        uuid=p.primary_category)
                    page = self.get_or_create(ArticlePage, p, section)
                except SectionPage.DoesNotExist:
                    print "couldn't find primary category ", \
                        p.primary_category, \
                        SectionPage.objects.all().values('uuid')
                    return None
            else:
                # special case for articles with no primary category
                # this assumption is probably wrong..
                # but we have no where else to put them
                main = Main.objects.all().first()
                page = self.get_or_create(FooterPage, p, main)
        else:
            try:
                main_instance = ArticlePage.objects.get(
                    uuid=p.source).specific
                page = self.get_or_create_translation(
                    main_instance.__class__, p, main_instance.get_parent(),
                    site_language)
                PageTranslation.objects.get_or_create(
                    page=main_instance,
                    translated_page=page)
            except ArticlePage.DoesNotExist:
                print "No source found for: ", p.source, (
                    ArticlePage.objects.all().values('uuid'))
                return None

        page.subtitle = p.subtitle
        page.body = json.dumps([
            {'type': 'paragraph', 'value': p.description},
            {'type': 'paragraph', 'value': p.content}
        ])
        is_featured = p.featured if p.featured else False
        is_featured_in_category = p.featured_in_category \
            if p.featured_in_category else False

        page.featured_in_latest = is_featured
        page.featured_in_homepage = is_featured_in_category
        for tag in p.author_tags:
            page.metadata_tags.add(tag)
        if p.image_host and p.image:
            page.image = get_image_file(p.image_host, p.image)

        page.save_revision().publish()

        return page

    def update_pages_with_linked_page_field(self):
        for p in self.ws.S(Page).all()[:10000]:
            if p.linked_pages:
                for lp in p.linked_pages:
                    try:
                        page = ArticlePage.objects.get(uuid=p.uuid)
                        page.body.stream_data.append(
                            {u'type': u'page',
                             u'value': ArticlePage.objects.get(uuid=lp).pk})
                        page.save_revision().publish()
                    except ArticlePage.DoesNotExist:
                        print 'Linked page does not exist %s' % lp

    def import_categories_for_child_language(
            self, category, selected_locale, site_language):
        if category.source:
            try:
                parent = SectionPage.objects.get(
                    uuid=category.source)
                translated_section = self.import_section_content(
                    category, site_language)
                PageTranslation.objects.get_or_create(
                    page=parent,
                    translated_page=translated_section)
            except SectionPage.DoesNotExist:
                print "couldn't find", category.source, (
                    SectionPage.objects.all().values('uuid'))
        else:
            print "no source found for: ", category.source, (
                SectionPage.objects.all().values('uuid'))

    def import_content_for(self, locales):
        for selected_locale in locales:

            site_language, _ = SiteLanguage.objects.get_or_create(
                locale=Locale.parse(selected_locale.get('locale')).language,
                is_main_language=selected_locale.get('is_main'))

            self.import_all_categories(site_language, selected_locale)
            self.import_all_pages(site_language, selected_locale)
        self.update_pages_with_linked_page_field()

    def import_all_categories(self, site_language, selected_locale):
        category_qs = self.ws.S(Category).filter(
            language=selected_locale.get('locale')
        ).order_by('position')[:10000]
        # S() only returns 10 results if you don't ask for more
        if site_language.is_main_language:
            for c in category_qs:
                self.import_section_content(c, site_language)
        else:
            for c in category_qs:
                self.import_categories_for_child_language(
                    c, selected_locale, site_language)

    def import_all_pages(self, site_language, selected_locale):
        for p in self.ws.S(Page).filter(
            language=selected_locale.get('locale')
        ).order_by('position')[:10000]:
            # S() only returns 10 results if you don't ask for more

            self.import_page_content(p, site_language)
