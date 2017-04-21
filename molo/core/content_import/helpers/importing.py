import json

from babel import Locale
from babel.core import UnknownLocaleError

from django.db.models.base import ValidationError

from unicore.content.models import Category, Page

from molo.core.models import (
    PageTranslation, SectionPage, ArticlePage, FooterPage,
    SectionIndexPage, FooterIndexPage, SiteLanguageRelation, Languages, Main)
from molo.core.content_import.helpers.get_image import get_image_file
from molo.core.content_import.helpers.locales import filter_locales_in_repo
from molo.core.content_import.utils import hash
from molo.core.utils import generate_slug


def import_repo(repo, main_locale, children, should_nest=False):
    children = filter_locales_in_repo(repo, children)

    for locale in [main_locale] + children:
        lang = create_language(repo, locale, locale == main_locale)
        index = get_or_create_index(repo, lang, should_nest)
        stray_index = get_or_create_stray_index(repo, lang, False)
        import_locale_content(repo, lang, index, stray_index)
        update_pages_with_linked_page_field(repo, locale)


def get_models(repo, cls, **kw):
    qs = repo.workspace.S(cls)
    qs = qs.filter(**kw)

    # S() only returns 10 results if you don't ask for more
    return qs.order_by('position').everything()


def get_sections_index():
    return SectionIndexPage.objects.live().first()


def get_footer_index():
    return FooterIndexPage.objects.live().first()


def get_or_create_index(repo, lang, should_nest):
    if should_nest:
        return repo_section_for_language(repo, lang)
    else:
        return get_sections_index()


def get_or_create_stray_index(repo, lang, should_nest):
    if should_nest:
        return get_or_create_index(repo, lang, should_nest)
    else:
        return get_footer_index()


def create_language(repo, locale, is_main):
    main = Main.objects.all().first()
    language_setting, _ = Languages.objects.get_or_create(
        site_id=main.get_site().pk)
    try:
        language, _ = SiteLanguageRelation.objects.get_or_create(
            language_setting=language_setting,
            locale=Locale.parse(locale).language,
            is_main_language=is_main,
            is_active=True)
    except UnknownLocaleError:
        language, _ = SiteLanguageRelation.objects.get_or_create(
            language_setting=language_setting,
            locale=locale.replace('_', '-'),
            is_main_language=False,
            is_active=True)

    return {
        'locale': locale,
        'language': language,
    }


def import_locale_content(repo, lang, index, stray_index):
    import_all_categories(repo, lang, index)
    import_all_pages(repo, lang, stray_index)


def repo_section_datum(repo, lang):
    # NOTE For sections that correspond to a repository (for the multi-repo
    # import case), We can't simply rely on the ORM to create a uuid for us,
    # since we need to retrieve the section if it already exists instead of
    # creating it again. This means we need to find the section by its
    # corresponding repository's name and the locale that the section was
    # created for. At the moment, we use the uuid field for this, though isn't
    # quite right -- uuid's need to be universally unique. A more robust
    # solution might be to support a metadata field on the SectionPage model
    # and query by this field for this case

    # NOTE At the moment, we are using the repository title as the title for
    # the corresponding section we create, regardless of the language the
    # section is created for. We need a way of creating a title from the
    # repository in the given language
    return {
        'uuid': hash((repo.name, lang['locale'])),
        'title': repo.title
    }


def repo_section_for_language(repo, lang):
    datum = repo_section_datum(repo, lang)
    index = get_sections_index()

    if is_main_language(lang):
        return get_or_create(SectionPage, index, **datum)
    else:
        return get_or_create_translation(SectionPage, lang, index, **datum)


def import_categories_for_child_language(repo, category, lang, index):
    if category.source:
        try:
            main_lang_page = SectionPage.objects.get(uuid=category.source)
            translated_section = import_section_content(
                repo, category, lang, index)
            PageTranslation.objects.get_or_create(
                page=main_lang_page,
                translated_page=translated_section)
        except SectionPage.DoesNotExist:
            print "couldn't find", category.source, (
                SectionPage.objects.all().values('uuid'))
    else:
        print "no source found for: ", category.source, (
            SectionPage.objects.all().values('uuid'))


def import_all_categories(repo, lang, index):
    category_qs = get_models(repo, Category, language=lang['locale'])

    if lang['language'].is_main_language:
        import_fn = import_section_content
    else:
        import_fn = import_categories_for_child_language

    for c in category_qs:
        import_fn(repo, c, lang, index)


def import_all_pages(repo, lang, stray_index):
    for p in get_models(repo, Page, language=lang['locale']):
        import_page_content(repo, p, lang, stray_index)


def is_main_language(lang):
    return lang['language'].is_main_language


def get_or_create_from_model(cls, obj, parent):
    return get_or_create(cls, parent, obj.uuid, obj.title)


def get_or_create_translation_from_model(cls, obj, lang, parent):
    return get_or_create_translation(cls, lang, parent, obj.uuid, obj.title)


def get_or_create(cls, parent, uuid, title):
    if cls.objects.filter(uuid=uuid).exists():
        return cls.objects.get(uuid=uuid)

    instance = cls(uuid=uuid, title=title)

    try:
        parent.add_child(instance=instance)
    except ValidationError:
        # non-ascii titles need slugs to be manually generated
        instance.slug = generate_slug(title)
        parent.add_child(instance=instance)

    instance.save_revision().publish()
    return instance


def get_or_create_translation(cls, lang, parent, uuid, title):
    instance = get_or_create(cls, parent, uuid, title)

    language_relation = instance.languages.first()
    language_relation.language = lang['language']
    language_relation.save()

    return instance


def import_section_content(repo, c, lang, parent):
    if is_main_language(lang):
        section = get_or_create_from_model(SectionPage, c, parent)
    else:
        section = get_or_create_translation_from_model(
            SectionPage, c, lang, parent)

    section.description = c.subtitle
    if c.image_host and c.image:
        section.image = get_image_file(c.image_host, c.image)

    section.save_revision().publish()

    return section


def import_page_content(repo, p, lang, stray_index):
    if is_main_language(lang):
        if p.primary_category:
            try:
                section = SectionPage.objects.get(uuid=p.primary_category)
                page = get_or_create_from_model(ArticlePage, p, section)
            except SectionPage.DoesNotExist:
                print "couldn't find primary category ", \
                    p.primary_category, \
                    SectionPage.objects.all().values('uuid')
                return None
        else:
            # special case for articles with no primary category
            # this assumption is probably wrong..
            # but we have no where else to put them
            page = get_or_create_from_model(FooterPage, p, stray_index)
    else:
        try:
            main_instance = ArticlePage.objects.get(uuid=p.source).specific

            page = get_or_create_translation_from_model(
                main_instance.__class__, p, lang, main_instance.get_parent())

            PageTranslation.objects.get_or_create(
                page=main_instance,
                translated_page=page)
        except ArticlePage.DoesNotExist:
            print "No source found for: ", p.source, (
                ArticlePage.objects.all().values('uuid'))
            return None

    page.subtitle = p.description
    page.body = json.dumps([{
        'type': 'paragraph',
        'value': p.content
    }])

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


def update_pages_with_linked_page_field(repo, locale):
    for p in repo.workspace.S(Page).filter(language=locale).everything():
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
