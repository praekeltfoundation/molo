from django.utils import timezone

from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, StreamFieldPanel, PageChooserPanel,
    MultiFieldPanel, InlinePanel, TabbedInterface, ObjectList)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailadmin.taggable import TagSearchable

from molo.core.blocks import MarkDownBlock
from molo.core import constants


class CommentedPageMixin(object):
    def get_effective_commenting_settings(self):
        # return commenting settings for the homepage
        if self.commenting_state:
            return {
                'state': self.commenting_state,
                'open_time': self.commenting_open_time,
                'close_time': self.commenting_close_time
            }
        # use the commenting settings for the parent page
        parent_page = Page.objects.all().ancestor_of(self).last()
        if parent_page:
            parent = parent_page.specific
            return parent.get_effective_commenting_settings()
        # add a default in case nothing is set. We should never get here
        return {
            'state': constants.COMMENTING_DISABLED,
            'open_time': None,
            'close_time': None
        }


class TranslatablePageMixin(models.Model):
    language = models.ForeignKey(
        'SiteLanguage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'is_main_language': True},
    )

    def save(self, *args, **kwargs):
        if (SiteLanguage.objects.filter(is_main_language=True).exists() and
                not self.language):
            self.language = SiteLanguage.objects.filter(
                is_main_language=True).first()

        return super(TranslatablePageMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class PageTranslation(models.Model):
    page = ParentalKey('wagtailcore.Page', related_name='translations')
    translated_page = models.ForeignKey('wagtailcore.Page', related_name='+')

    panels = [
        PageChooserPanel('translated_page', 'wagtailcore.Page'),
    ]


class HomePage(CommentedPageMixin, TranslatablePageMixin, Page):
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

    commenting_state = models.CharField(
        max_length=1,
        choices=constants.COMMENTING_STATE_CHOICES,
        blank=True,
        null=True)
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

    parent_page_types = ['core.Main']
    subpage_types = ['core.ArticlePage']

    translation_panels = ([
        InlinePanel('translations', label="Translations"),
    ])

HomePage.content_panels = [
    FieldPanel('title', classname='full title'),
    ImageChooserPanel('banner'),
    PageChooserPanel('banner_link_page'),
    MultiFieldPanel(
        [
            FieldPanel('commenting_state'),
            FieldPanel('commenting_open_time'),
            FieldPanel('commenting_close_time'),
        ],
        heading="Commenting Settings",)
]

HomePage.edit_handler = TabbedInterface([
    ObjectList(HomePage.content_panels, heading='Content'),
    ObjectList(HomePage.promote_panels, heading='Promote'),
    ObjectList(HomePage.translation_panels, heading='Translation'),
    ObjectList(HomePage.settings_panels, heading='Settings',
               classname="settings"),

])


class Main(CommentedPageMixin, Page):
    parent_page_types = []
    subpage_types = ['core.HomePage', 'core.SectionPage',
                     'core.FooterPage']
    commenting_state = models.CharField(
        max_length=1,
        choices=constants.COMMENTING_STATE_CHOICES,
        blank=False,
        default='C')
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

Main.content_panels = [
    MultiFieldPanel(
        [
            FieldPanel('commenting_state'),
            FieldPanel('commenting_open_time'),
            FieldPanel('commenting_close_time'),
        ],
        heading="Commenting Settings",)
]


class LanguagePage(CommentedPageMixin, Page):
    code = models.CharField(
        max_length=255,
        help_text=_('The language code as specified in iso639-2'))

    parent_page_types = ['core.Main']
    subpage_types = []

    commenting_state = models.CharField(
        max_length=1,
        choices=constants.COMMENTING_STATE_CHOICES,
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
            featured_in_latest=True).order_by('-latest_revision_created_at')

    def footers(self):
        return FooterPage.objects.live().child_of(self)

    class Meta:
        verbose_name = _('Language')

LanguagePage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('code'),

    MultiFieldPanel(
        [
            FieldPanel('commenting_state'),
            FieldPanel('commenting_open_time'),
            FieldPanel('commenting_close_time'),
        ],
        heading="Commenting Settings",)
]


class SiteLanguage(models.Model):
    title = models.CharField(
        verbose_name=_('language name'),
        max_length=255,
        blank=False,
        help_text=_("The page title as you'd like it to be seen by the public")
    )

    code = models.CharField(
        max_length=255,
        verbose_name=_('language code'),
        help_text=_('The language code as specified in iso639-2'))

    is_main_language = models.BooleanField(
        default=False,
        editable=False,
        verbose_name=_('main Language'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('active Language'),
    )

    def save(self, *args, **kwargs):
        if SiteLanguage.objects.filter(is_main_language=True).exists():
            return super(SiteLanguage, self).save(*args, **kwargs)

        self.is_main_language = True
        return super(SiteLanguage, self).save(*args, **kwargs)

    def __str__(self):
        return "%s" % (self.title,)

    class Meta:
        verbose_name = _('Language')


class SectionPage(CommentedPageMixin, TranslatablePageMixin, Page):
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

    commenting_state = models.CharField(
        max_length=1,
        choices=constants.COMMENTING_STATE_CHOICES,
        blank=True,
        null=True)
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

    translation_panels = ([
        InlinePanel('translations', label="Translations"),
    ])

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

    class Meta:
        verbose_name = _('Section')

SectionPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('description'),
    ImageChooserPanel('image'),
    MultiFieldPanel(
        [
            FieldPanel('commenting_state'),
            FieldPanel('commenting_open_time'),
            FieldPanel('commenting_close_time'),
        ],
        heading="Commenting Settings",)
]

SectionPage.settings_panels = [
    MultiFieldPanel(
        Page.settings_panels, "Scheduled publishing", "publishing"),
    MultiFieldPanel(
        [FieldRowPanel(
            [FieldPanel('extra_style_hints')], classname="label-above")],
        "Meta")
]

SectionPage.edit_handler = TabbedInterface([
    ObjectList(SectionPage.content_panels, heading='Content'),
    ObjectList(SectionPage.promote_panels, heading='Promote'),
    ObjectList(SectionPage.translation_panels, heading='Translation'),
    ObjectList(SectionPage.settings_panels, heading='Settings',
               classname="settings"),

])


class ArticlePageTag(TaggedItemBase):
    content_object = ParentalKey(
        'core.ArticlePage', related_name='tagged_items')


class ArticlePage(CommentedPageMixin, TranslatablePageMixin, Page,
                  TagSearchable):
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
    tags = ClusterTaggableManager(through=ArticlePageTag, blank=True)

    subpage_types = []
    search_fields = Page.search_fields + TagSearchable.search_fields + (
        index.SearchField('subtitle'),
        index.SearchField('body'),
    )

    commenting_state = models.CharField(
        max_length=1,
        choices=constants.COMMENTING_STATE_CHOICES,
        blank=True,
        null=True)
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

    featured_promote_panels = [
        FieldPanel('featured_in_latest'),
        FieldPanel('featured_in_section'),
        FieldPanel('featured_in_homepage'),
    ]

    translation_panels = ([
        InlinePanel('translations', label="Translations"),
    ])

    def get_absolute_url(self):  # pragma: no cover
        return self.url

    def get_parent_section(self):
        return SectionPage.objects.all().ancestor_of(self).last()

    def allow_commenting(self):
        commenting_settings = self.get_effective_commenting_settings()
        if (commenting_settings['state'] != constants.COMMENTING_OPEN):
            now = timezone.now()
            if (commenting_settings['state'] ==
                    constants.COMMENTING_TIMESTAMPED):
                # Allow commenting over the given time period
                open_time = commenting_settings['open_time']
                close_time = commenting_settings['close_time']
                return open_time < now < close_time
            if (commenting_settings['state'] == constants.COMMENTING_CLOSED or
                    commenting_settings['state'] ==
                    constants.COMMENTING_DISABLED):
                # Allow automated reopening of commenting at a specified time
                reopen_time = commenting_settings['open_time']
                if (reopen_time):
                    if reopen_time < now:
                        self.commenting_state = constants.COMMENTING_OPEN
                        self.save()
                        return True
            return False
        return True

    def is_commenting_enabled(self):
        commenting_settings = self.get_effective_commenting_settings()
        if (commenting_settings['state'] == constants.COMMENTING_DISABLED or
                commenting_settings['state'] is None):
            return False
        return True

    class Meta:
        verbose_name = _('Article')

ArticlePage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('subtitle'),
    ImageChooserPanel('image'),
    StreamFieldPanel('body'),
    FieldPanel('tags'),
    MultiFieldPanel(
        [
            FieldPanel('commenting_state'),
            FieldPanel('commenting_open_time'),
            FieldPanel('commenting_close_time'),
        ],
        heading="Commenting Settings",)
]

ArticlePage.promote_panels = [
    MultiFieldPanel(ArticlePage.featured_promote_panels, "Featuring"),
    MultiFieldPanel(
        Page.promote_panels,
        "Common page configuration", "collapsible collapsed")]

ArticlePage.edit_handler = TabbedInterface([
    ObjectList(ArticlePage.content_panels, heading='Content'),
    ObjectList(ArticlePage.promote_panels, heading='Promote'),
    ObjectList(ArticlePage.translation_panels, heading='Translation'),
    ObjectList(ArticlePage.settings_panels, heading='Settings',
               classname="settings"),

])


class FooterPage(ArticlePage):
    parent_page_types = ['core.Main']
    subpage_types = []

FooterPage.content_panels = ArticlePage.content_panels
