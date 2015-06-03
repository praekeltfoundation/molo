from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


class HomePage(Page):
    pass


class Main(Page):
    parent_page_types = []
    subpage_types = ['core.LanguagePage']


class LanguagePage(Page):
    code = models.CharField(max_length=255)

    parent_page_types = ['core.Main']
    subpage_types = ['core.HomePage', 'core.SectionPage']

    class Meta:
        verbose_name = 'Language'

LanguagePage.content_panels = [
    FieldPanel('title'),
    FieldPanel('code'),
]


class SectionPage(Page):
    description = models.TextField(null=True, blank=True)

    subpage_types = ['core.ArticlePage']
    search_fields = Page.search_fields + (
        index.SearchField('description'),
    )

    class Meta:
        verbose_name = 'Section'

SectionPage.content_panels = [
    FieldPanel('title'),
    FieldPanel('description'),
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

    subpage_types = []
    search_fields = Page.search_fields + (
        index.SearchField('subtitle'),
    )

    class Meta:
        verbose_name = 'Article'

ArticlePage.content_panels = [
    FieldPanel('title'),
    FieldPanel('subtitle'),
    ImageChooserPanel('image'),
]
