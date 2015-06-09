from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock

from molo.core.blocks import MarkDownBlock


class HomePage(Page):
    pass


class Main(Page):
    parent_page_types = []
    subpage_types = ['core.LanguagePage']


class LanguagePage(Page):
    code = models.CharField(
        max_length=255,
        help_text=_('The language code as specified in iso639-2'))

    parent_page_types = ['core.Main']
    subpage_types = ['core.HomePage', 'core.SectionPage']

    def sections(self):
        return SectionPage.objects.live().child_of(self)

    class Meta:
        verbose_name = _('Language')

LanguagePage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('code'),
]


class SectionPage(Page):
    description = models.TextField(null=True, blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    subpage_types = ['core.ArticlePage', 'core.SectionPage']
    search_fields = Page.search_fields + (
        index.SearchField('description'),
    )

    def articles(self):
        return ArticlePage.objects.live().child_of(self)

    def sections(self):
        return SectionPage.objects.live().child_of(self)

    def featured_articles(self):
        # Get list of live article pages that are descendants of this page
        # and are "featured in menu"
        return self.articles().in_menu()

    class Meta:
        verbose_name = _('Section')

SectionPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('description'),
    ImageChooserPanel('image'),
]


class ArticlePage(Page):
    subtitle = models.TextField(null=True, blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', MarkDownBlock()),
        ('image', ImageChooserBlock()),
        ('list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('numbered_list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('page', blocks.PageChooserBlock()),
    ], null=True, blank=True)

    subpage_types = []
    search_fields = Page.search_fields + (
        index.SearchField('subtitle'),
    )

    class Meta:
        verbose_name = _('Article')

ArticlePage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('subtitle'),
    ImageChooserPanel('image'),
    StreamFieldPanel('body'),
]
