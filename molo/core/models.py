from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, StreamFieldPanel, PageChooserPanel,
    MultiFieldPanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock

from molo.core.blocks import MarkDownBlock


class HomePage(Page):
    banner = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    banner_link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Optional page to which the banner will link to')
    )

    COMMENTING_STATE_CHOICES = (
        ('O', 'Open'),
        ('C', 'Closed'),
        ('T', 'Timestamped'),
    )
    commenting_state = models.CharField(max_length=1,
                                      choices=COMMENTING_STATE_CHOICES,
                                      blank=True,
                                      null=True)
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

    parent_page_types = ['core.LanguagePage']
    subpage_types = ['core.ArticlePage']

    def get_effective_commenting_settings(self):
        # return commenting settings for the homepage
        if (self.commenting_state and self.commenting_state != ""):
            return {
                'state': self.commenting_state,
                'open_time': self.commenting_open_time,
                'close_time': self.commenting_close_time
            }
        # use the commenting settings for the language page
        language_page = LanguagePage.objects.all().ancestor_of(self).last()
        return language_page.get_effective_commenting_settings()

HomePage.content_panels = [
    FieldPanel('title', classname='full title'),
    ImageChooserPanel('banner'),
    PageChooserPanel('banner_link_page'),
]


class Main(Page):
    parent_page_types = []
    subpage_types = ['core.LanguagePage']

    COMMENTING_STATE_CHOICES = (
        ('O', 'Open'),
        ('C', 'Closed'),
        ('T', 'Timestamped'),
    )
    commenting_state = models.CharField(max_length=1,
                                      choices=COMMENTING_STATE_CHOICES,
                                      blank=False,
                                      default='C')
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)


class LanguagePage(Page):
    code = models.CharField(
        max_length=255,
        help_text=_('The language code as specified in iso639-2'))

    parent_page_types = ['core.Main']
    subpage_types = ['core.HomePage', 'core.SectionPage', 'core.FooterPage']

    COMMENTING_STATE_CHOICES = (
        ('O', 'Open'),
        ('C', 'Closed'),
        ('T', 'Timestamped'),
    )
    commenting_state = models.CharField(max_length=1,
                                      choices=COMMENTING_STATE_CHOICES,
                                      blank=True,
                                      null=True)
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

    def homepages(self):
        return HomePage.objects.live().child_of(self)

    def sections(self):
        return SectionPage.objects.live().child_of(self)

    def latest_articles(self):
        return ArticlePage.objects.live().descendant_of(self).filter(
            featured_in_latest=True).order_by('-first_published_at')

    def footers(self):
        return FooterPage.objects.live().child_of(self)

    def get_effective_commenting_settings(self):
        # return commenting settings for this language
        if (self.commenting_state and self.commenting_state != ""):
            return {
                'state': self.commenting_state,
                'open_time': self.commenting_open_time,
                'close_time': self.commenting_close_time
            }
        # use the commenting settings for the Home page
        main = Main.objects.all().ancestor_of(self).last()
        return {
            'state': main.commenting_state,
            'open_time': main.commenting_open_time,
            'close_time': main.commenting_close_time
        }

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
    extra_style_hints = models.TextField(
        default='',
        null=True, blank=True,
        help_text=_(
            "Styling options that can be applied to this section "
            "and all its descendants"))

    COMMENTING_STATE_CHOICES = (
        ('O', 'Open'),
        ('C', 'Closed'),
        ('T', 'Timestamped'),
    )
    commenting_state = models.CharField(max_length=1,
                                      choices=COMMENTING_STATE_CHOICES,
                                      blank=True,
                                      null=True)
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

    def articles(self):
        return ArticlePage.objects.live().child_of(self)

    def sections(self):
        return SectionPage.objects.live().child_of(self)

    def featured_articles(self):
        return self.articles().filter(featured_in_section=True)

    def featured_articles_in_homepage(self):
        qs = ArticlePage.objects.live().order_by('-first_published_at')
        return qs.descendant_of(self).filter(featured_in_homepage=True)

    def latest_articles_in_homepage(self):
        qs = ArticlePage.objects.live().order_by('-first_published_at')
        return qs.descendant_of(self).filter(featured_in_latest=True)

    def get_effective_extra_style_hints(self):
        # The extra css is inherited from the parent SectionPage.
        # This will either return the current value or a value
        # from its parents.
        parent_section = SectionPage.objects.all().ancestor_of(self).last()
        if parent_section:
            return self.extra_style_hints or \
                parent_section.get_effective_extra_style_hints()
        else:
            return self.extra_style_hints

    def get_effective_image(self):

        parent_section = SectionPage.objects.all().ancestor_of(self).last()
        if parent_section:
            return self.image or \
                parent_section.get_effective_image()
        else:
            return self.image

    def get_parent_section(self):
        return SectionPage.objects.all().ancestor_of(self).last()

    def get_effective_commenting_settings(self):
        # return commenting settings for this section
        if (self.commenting_state and self.commenting_state != ""):
            return {
                'state': self.commenting_state,
                'open_time': self.commenting_open_time,
                'close_time': self.commenting_close_time
            }
        # check parent sections for commenting settings
        parent_section = SectionPage.objects.all().ancestor_of(self).last()
        if parent_section:
            return parent_section.get_effective_commenting_settings()
        # use the commenting settings for the language page
        language_page = LanguagePage.objects.all().ancestor_of(self).last()
        return language_page.get_effective_commenting_settings()

    class Meta:
        verbose_name = _('Section')

SectionPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('description'),
    ImageChooserPanel('image'),
]

SectionPage.settings_panels = [
    MultiFieldPanel(
        Page.settings_panels, "Scheduled publishing", "publishing"),
    MultiFieldPanel(
        [FieldRowPanel(
            [FieldPanel('extra_style_hints')], classname="label-above")],
        "Meta")
]


class ArticlePage(Page):
    subtitle = models.TextField(null=True, blank=True)
    featured_in_latest = models.BooleanField(
        default=False,
        help_text=_("Article to be featured in the Latest module"))
    featured_in_section = models.BooleanField(
        default=False,
        help_text=_("Article to be featured in the Section module"))
    featured_in_homepage = models.BooleanField(
        default=False,
        help_text=_(
            "Article to be featured in the Homepage "
            "within the Section module"))
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
        index.SearchField('body'),
    )

    COMMENTING_STATE_CHOICES = (
        ('O', 'Open'),
        ('C', 'Closed'),
        ('T', 'Timestamped'),
    )
    commenting_state = models.CharField(max_length=1,
                                      choices=COMMENTING_STATE_CHOICES,
                                      blank=True,
                                      null=True)
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

    featured_promote_panels = [
        FieldPanel('featured_in_latest'),
        FieldPanel('featured_in_section'),
        FieldPanel('featured_in_homepage'),
    ]

    def get_absolute_url(self):  # pragma: no cover
        return self.url

    def get_parent_section(self):
        return SectionPage.objects.all().ancestor_of(self).last()

    def get_effective_commenting_settings(self):
        # return commenting settings for this section
        if (self.commenting_state and self.commenting_state != ""):
            return {
                'state': self.commenting_state,
                'open_time': self.commenting_open_time,
                'close_time': self.commenting_close_time
            }
        # use the commenting settings for the parent section
        return self.get_parent_section().get_effective_commenting_settings()

    class Meta:
        verbose_name = _('Article')

ArticlePage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('subtitle'),
    ImageChooserPanel('image'),
    StreamFieldPanel('body'),
]

ArticlePage.promote_panels = [
    MultiFieldPanel(ArticlePage.featured_promote_panels, "Featuring"),
    MultiFieldPanel(
        Page.promote_panels,
        "Common page configuration", "collapsible collapsed")]


class FooterPage(ArticlePage):
    parent_page_types = ['core.LanguagePage']
    subpage_types = []

FooterPage.content_panels = ArticlePage.content_panels
