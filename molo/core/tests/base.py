import json

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from wagtail.wagtailcore.models import Site, Page, Collection

from molo.core.models import (Main, SectionPage, ArticlePage, PageTranslation,
                              SectionIndexPage, FooterIndexPage,
                              BannerIndexPage)
from molo.core.utils import generate_slug


class MoloTestCaseMixin(object):
    def login(self):
        # Create a user
        user = get_user_model().objects.create_superuser(
            username='superuser', email='superuser@email.com', password='pass')

        # Login
        self.client.login(username='superuser', password='pass')

        return user

    def mk_main(self):
        # Create page content type
        page_content_type, created = ContentType.objects.get_or_create(
            model='page',
            app_label='wagtailcore'
        )

        # Create root page
        self.root = Page.objects.create(
            title="Root",
            slug='root',
            content_type=page_content_type,
            path='0001',
            depth=1,
            numchild=1,
            url_path='/',
        )

        main_content_type, created = ContentType.objects.get_or_create(
            model='main', app_label='core')

        # Create a new homepage
        self.main = Main.objects.create(
            title="Main",
            slug='main',
            content_type=main_content_type,
            path='00010001',
            depth=2,
            numchild=0,
            url_path='/home/',
        )
        self.main.save_revision().publish()

        # Create index pages
        self.section_index = SectionIndexPage(title='Sections',
                                              slug='sections')
        self.main.add_child(instance=self.section_index)
        self.section_index.save_revision().publish()

        self.footer_index = FooterIndexPage(title='Footer pages',
                                            slug='footer-pages')
        self.main.add_child(instance=self.footer_index)
        self.footer_index.save_revision().publish()

        self.banner_index = BannerIndexPage(title='Banners', slug='banners')
        self.main.add_child(instance=self.banner_index)
        self.banner_index.save_revision().publish()

        # Create root collection
        Collection.objects.create(
            name="Root",
            path='0001',
            depth=1,
            numchild=0,
        )

        # Create a site with the new homepage set as the root
        Site.objects.all().delete()
        self.site = Site.objects.create(
            hostname='localhost', root_page=self.main, is_default_site=True)

    def mk_sections(self, parent, count=2, **kwargs):
        sections = []

        for i in range(count):
            data = {}
            data.update({
                'title': 'Test Section %s' % (i, ),
            })
            data.update(kwargs)
            data.update({
                'slug': generate_slug(data['title'])
            })
            section = SectionPage(**data)
            parent.add_child(instance=section)
            section.save_revision().publish()
            sections.append(section)
        return sections

    def mk_articles(self, parent, count=2, **kwargs):
        articles = []

        for i in range(count):
            data = {}
            data.update({
                'title': 'Test page %s' % (i, ),
                'subtitle': 'Sample page description for %s' % (i, ),
                'body': json.dumps([{
                    'type': 'paragraph',
                    'value': 'Sample page content for %s' % (i, )}]),
            })
            data.update(kwargs)
            data.update({
                'slug': generate_slug(data['title'])
            })
            article = ArticlePage(**data)
            parent.add_child(instance=article)
            article.save_revision().publish()
            articles.append(article)
        return articles

    def mk_section(self, parent, **kwargs):
        return self.mk_sections(parent, count=1, **kwargs)[0]

    def mk_article(self, parent, **kwargs):
        return self.mk_articles(parent, count=1, **kwargs)[0]

    def mk_translation(self, source, language, translation):
        language_relation = translation.languages.first()
        language_relation.language = language
        language_relation.save()
        translation.save_revision().publish()
        PageTranslation.objects.get_or_create(
            page=source, translated_page=translation)
        return translation

    def mk_section_translation(self, source, language, **kwargs):
        instance = self.mk_section(source.get_parent(), **kwargs)
        return self.mk_translation(source, language, instance)

    def mk_article_translation(self, source, language, **kwargs):
        instance = self.mk_article(source.get_parent(), **kwargs)
        return self.mk_translation(source, language, instance)
