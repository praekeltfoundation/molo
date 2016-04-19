from babel import Locale

from molo.core.models import SiteLanguage

from unicore.content.models import Category, Page


class ContentImportValidation(object):
    errors = []

    def __init__(self, repo):
        self.repo = repo
        self.ws = self.repo.workspace

    def validate_for(self, main, children):
        self.errors = []

        self.validate_wagtail_has_no_language(main)
        for l in [main] + children:
            self.validate_translated_content_has_source(l, main)
            self.validate_page_primary_category_exists(l)
            self.validate_translated_content_source_exists(l, main)

        return self.errors

    def validate_wagtail_has_no_language(self, main):
        main = Locale.parse(main).language

        wagtail_main_language = SiteLanguage.objects.filter(
            is_main_language=True).first()
        if (wagtail_main_language and not
                wagtail_main_language.locale == main):
            self.errors.append({
                'type': 'wrong_main_language_exist_in_wagtail',
                'details': {
                    'repo': self.repo.name,
                    'lang': wagtail_main_language.get_locale_display(),
                    'selected_lang': Locale.parse(main).english_name
                }})

    def validate_translated_content_has_source(self, locale, main):
        if locale != main:
            categories = self.ws.S(Category).filter(
                language=locale).order_by('position')[:10000]
            for c in categories:
                if not c.source:
                    self.errors.append({
                        'type': 'no_source_found_for_category',
                        'details': {
                            'repo': self.repo.name,
                            'category': c.title,
                            'lang': Locale.parse(locale).english_name
                        }})

            pages = self.ws.S(Page).filter(language=locale)[:10000]
            for p in pages:
                if not p.source:
                    self.errors.append({
                        'type': 'no_source_found_for_page',
                        'details': {
                            'repo': self.repo.name,
                            'article': p.title,
                            'lang': Locale.parse(locale).english_name
                        }})

    def validate_translated_content_source_exists(self, locale, main):
        if locale != main:
            categories = self.ws.S(Category).filter(
                language=locale).order_by('position')[:10000]
            for c in categories:
                if c.source and not self.validate_source_exists(
                        Category, c.source, main):
                    self.errors.append({
                        'type': 'category_source_not_exists',
                        'details': {
                            'repo': self.repo.name,
                            'category': c.title,
                            'lang': Locale.parse(locale).english_name
                        }})

            pages = self.ws.S(Page).filter(language=locale)[:10000]
            for p in pages:
                if p.source and not self.validate_source_exists(
                        Page, p.source, main):
                    self.errors.append({
                        'type': 'page_source_not_exists',
                        'details': {
                            'repo': self.repo.name,
                            'page': p.title,
                            'lang': Locale.parse(locale).english_name
                        }})

    def validate_page_primary_category_exists(self, locale):
        pages = self.ws.S(Page).filter(language=locale)[:10000]
        for p in pages:
            if p.primary_category and not self.validate_category_exists(
                    p.primary_category, locale):
                self.errors.append({
                    'type': 'no_primary_category',
                    'details': {
                        'repo': self.repo.name,
                        'article': p.title,
                        'lang': Locale.parse(locale).english_name
                    }})

    def validate_category_exists(self, uuid, locale):
        return self.ws.S(Category).filter(
            language=locale, uuid=uuid).count() > 0

    def validate_source_exists(self, cls, uuid, locale):
        return self.ws.S(cls).filter(
            language=locale, uuid=uuid).count() > 0
