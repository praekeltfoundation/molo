import json

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from wagtail.wagtailcore.models import Page, Collection

from molo.core.models import (Main, SectionPage, ArticlePage, PageTranslation,
                              SectionIndexPage, FooterIndexPage,
                              BannerIndexPage, TagIndexPage, Tag,
                              ReactionQuestionIndexPage,
                              ArticlePageReactionQuestions, ReactionQuestion,
                              ReactionQuestionChoice)
from molo.core.utils import generate_slug


class MoloTestCaseMixin(object):
    def login(self):
        # Create a user
        user = get_user_model().objects.create_superuser(
            username='superuser', email='superuser@email.com', password='pass')

        # Login
        self.client.login(username='superuser', password='pass')

        return user

    def mk_root(self):
        page_content_type, created = ContentType.objects.get_or_create(
            model='page',
            app_label='wagtailcore'
        )
        self.root, _ = Page.objects.get_or_create(
            title="Root",
            slug='root',
            content_type=page_content_type,
            path='0001',
            depth=1,
            numchild=1,
            url_path='/',
        )

    def mk_main(self, title='Main', slug='main'):
        self.mk_root()
        main_content_type, created = ContentType.objects.get_or_create(
            model='main', app_label='core')

        # Create a new homepage
        self.main = Main.objects.create(
            title=title,
            slug=slug,
            content_type=main_content_type,
            path='00010001',
            depth=2,
            numchild=0,
            url_path='/home/',
        )
        self.main.save_revision().publish()
        self.main.save()

        # Create index pages
        self.section_index = SectionIndexPage.objects.child_of(
            self.main).first()

        self.reaction_index = ReactionQuestionIndexPage.objects.child_of(
            self.main).first()

        self.footer_index = FooterIndexPage.objects.child_of(self.main).first()

        self.banner_index = BannerIndexPage.objects.child_of(self.main).first()

        self.tag_index = TagIndexPage.objects.child_of(self.main).first()

        # Create root collection
        Collection.objects.create(
            name="Root",
            path='0001',
            depth=1,
            numchild=0,
        )

        # Create a site with the new homepage set as the root
        # Site.objects.all().delete()
        self.site = self.main.get_site()

    def mk_main2(self, title='main2', slug='main2', path=00010002):
        self.mk_root()
        main_content_type, created = ContentType.objects.get_or_create(
            model='main', app_label='core')

        # Create a new homepage
        self.main2 = Main.objects.create(
            title=title,
            slug=slug,
            content_type=main_content_type,
            path=path,
            depth=2,
            numchild=0,
            url_path='/main2/',
        )
        self.main2.save_revision().publish()
        self.main2.save()

        # Create index pages
        self.section_index2 = SectionIndexPage.objects.child_of(
            self.main2).first()

        self.reaction_index2 = ReactionQuestionIndexPage.objects.child_of(
            self.main2).first()

        self.footer_index2 = FooterIndexPage.objects.child_of(
            self.main2).first()

        self.banner_index2 = BannerIndexPage.objects.child_of(
            self.main2).first()

        self.tag_index2 = TagIndexPage.objects.child_of(
            self.main2).first()

        # Create root collection
        Collection.objects.get_or_create(
            name="Root",
            path='0001',
            depth=1,
            numchild=0,
        )

        # Create a site with the new homepage set as the root
        # Site.objects.all().delete()
        self.site2 = self.main2.get_site()

    def mk_tag(self, parent, **kwargs):
        data = {}
        data.update({
            'title': 'Test Tag',
        })
        data.update(kwargs)
        data.update({
            'slug': generate_slug(data['title'])
        })
        tag = Tag(**data)
        parent.add_child(instance=tag)
        tag.save_revision().publish()
        return tag

    def mk_reaction_question(self, parent, article, **kwargs):
        data = {}
        data.update({
            'title': 'Test Question',
        })
        data.update(kwargs)
        data.update({
            'slug': generate_slug(data['title'])
        })
        question = ReactionQuestion(**data)
        parent.add_child(instance=question)
        question.save_revision().publish()
        choice1 = ReactionQuestionChoice(
            title='yes', success_message='well done')
        question.add_child(instance=choice1)
        choice1.save_revision().publish()
        choice2 = ReactionQuestionChoice(title='maybe')
        question.add_child(instance=choice2)
        choice2.save_revision().publish()
        choice3 = ReactionQuestionChoice(title='no')
        question.add_child(instance=choice3)
        choice3.save_revision().publish()
        ArticlePageReactionQuestions.objects.create(
            reaction_question=question, page=article)
        return question

    def mk_sections(self, parent, count=2, **kwargs):
        sections = []
        for i in range(count):
            data = {}
            data.update({
                'title': 'Test Section %s' % (i, ),
            })
            data.update(kwargs)
            data.update({
                'slug': generate_slug(data['title']),
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

    def mk_tag_translation(self, source, language, **kwargs):
        instance = self.mk_tag(source.get_parent(), **kwargs)
        return self.mk_translation(source, language, instance)

    def mk_reaction_translation(self, source, article, language, **kwargs):
        instance = self.mk_reaction_question(
            source.get_parent(), article, **kwargs)
        return self.mk_translation(source, language, instance)
