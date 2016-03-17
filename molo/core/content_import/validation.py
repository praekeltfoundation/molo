from babel import Locale

from molo.core.models import SiteLanguage

from unicore.content.models import Category, Page


class ContentImportValidation(object):
    errors = []

    def __init__(self, ws):
        self.ws = ws

    def is_validate_for(self, locales):
        self.errors = []
        for l in locales:
            if l.get('is_main'):
                main_language = l.get('locale')
                break

        self.validate_wagtail_has_no_language(main_language)
        for l in locales:
            self.validate_translated_content_has_source(l)
            self.validate_page_primary_category_exists(l)
            self.validate_translated_content_source_exists(l, main_language)

        return self.errors

    def validate_wagtail_has_no_language(self, main_language):
        main_language = Locale.parse(main_language).language

        wagtail_main_language = SiteLanguage.objects.filter(
            is_main_language=True).first()
        if (wagtail_main_language and not
                wagtail_main_language.locale == main_language):
            self.errors.append({
                'type': 'wrong_main_language_exist_in_wagtail',
                'details': {
                    'lang': wagtail_main_language.get_locale_display(),
                    'selected_lang': Locale.parse(main_language).english_name
                }})

    def validate_translated_content_has_source(self, l):
        if not l.get('is_main'):
            child_language = l.get('locale')

            categories = self.ws.S(Category).filter(
                language=child_language).order_by('position')[:10000]
            for c in categories:
                if not c.source:
                    self.errors.append({
                        'type': 'no_source_found_for_category',
                        'details': {
                            'category': c.title,
                            'lang': Locale.parse(child_language).english_name
                        }})

            pages = self.ws.S(Page).filter(language=child_language)[:10000]
            for p in pages:
                if not p.source:
                    self.errors.append({
                        'type': 'no_source_found_for_page',
                        'details': {
                            'article': p.title,
                            'lang': Locale.parse(child_language).english_name
                        }})

    def validate_translated_content_source_exists(self, l, main_language):
        if not l.get('is_main'):
            child_language = l.get('locale')

            categories = self.ws.S(Category).filter(
                language=child_language).order_by('position')[:10000]
            for c in categories:
                if c.source and not self.validate_source_exists(
                        Category, c.source, main_language):
                    self.errors.append({
                        'type': 'category_source_not_exists',
                        'details': {
                            'category': c.title,
                            'lang': Locale.parse(child_language).english_name
                        }})

            pages = self.ws.S(Page).filter(language=child_language)[:10000]
            for p in pages:
                if p.source and not self.validate_source_exists(
                        Page, p.source, main_language):
                    self.errors.append({
                        'type': 'page_source_not_exists',
                        'details': {
                            'page': p.title,
                            'lang': Locale.parse(child_language).english_name
                        }})

    def validate_page_primary_category_exists(self, l):
        language = l.get('locale')
        pages = self.ws.S(Page).filter(language=language)[:10000]
        for p in pages:
            if p.primary_category and not self.validate_category_exists(
                    p.primary_category, language):
                self.errors.append({
                    'type': 'no_primary_category',
                    'details': {
                        'article': p.title,
                        'lang': Locale.parse(language).english_name
                    }})

    def validate_category_exists(self, uuid, locale):
        return self.ws.S(Category).filter(
            language=locale, uuid=uuid).count() > 0

    def validate_source_exists(self, cls, uuid, locale):
        return self.ws.S(cls).filter(
            language=locale, uuid=uuid).count() > 0
