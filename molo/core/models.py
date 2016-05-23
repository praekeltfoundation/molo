from django.utils import timezone

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language_from_request
from django.shortcuts import redirect

from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, StreamFieldPanel, PageChooserPanel,
    MultiFieldPanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailadmin.taggable import TagSearchable

from molo.core.blocks import MarkDownBlock
from molo.core import constants
from molo.core.utils import get_locale_code

from django.core.validators import MaxValueValidator, MinValueValidator


@register_setting
class SiteSettings(BaseSetting):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    ga_tag_manager = models.CharField(
        verbose_name=_('GA Tag Manager'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("GA Tag Manager tracking code (e.g GTM-XXX)")
    )

    content_rotation = models.BooleanField(
        default=False,
        help_text=_(
            "This option allows content to be rotated randomly and"
            " automatically")
    )

    content_rotation_time = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(23),
            MinValueValidator(0)
        ],
        help_text=_(
            "This is the time that content will be rotated every day. "
            "If the content should rotate at 14h, then fill in 14")
    )

    panels = [
        ImageChooserPanel('logo'),
        FieldPanel('ga_tag_manager'),
        MultiFieldPanel(
            [
                FieldPanel('content_rotation'),
                FieldPanel('content_rotation_time'),
            ],
            heading="Content Rotation Settings",)
    ]


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


class PageTranslation(models.Model):
    page = models.ForeignKey('wagtailcore.Page', related_name='translations')
    translated_page = models.OneToOneField(
        'wagtailcore.Page', related_name='source_page')


class LanguageRelation(models.Model):
    page = models.ForeignKey('wagtailcore.Page', related_name='languages')
    language = models.ForeignKey('core.SiteLanguage', related_name='+')


class TranslatablePageMixin(object):

    def get_translation_for(self, locale, is_live=True):
        language = SiteLanguage.objects.filter(locale=locale).first()
        if not language:
            return None

        main_language_page = self.get_main_language_page()
        if language.is_main_language and not self == main_language_page:
            return main_language_page

        translated = None
        qs = self.specific.translations.all()
        if is_live is not None:
            qs = qs.filter(translated_page__live=True)

        for t in qs:
            if t.translated_page.languages.filter(
                    language__locale=locale).exists():
                translated = t.translated_page.languages.filter(
                    language__locale=locale).first().page.specific
                break
        return translated

    def get_main_language_page(self):
        if hasattr(self.specific, 'source_page') and self.specific.source_page:
            return self.specific.source_page.page
        return self

    def save(self, *args, **kwargs):
        response = super(TranslatablePageMixin, self).save(*args, **kwargs)

        if (SiteLanguage.objects.filter(is_main_language=True).exists() and
                not self.languages.exists()):
            LanguageRelation.objects.create(
                page=self,
                language=SiteLanguage.objects.filter(
                    is_main_language=True).first())
        return response

    def serve(self, request):
        locale_code = get_locale_code(get_language_from_request(request))
        translation = self.get_translation_for(locale_code)
        if translation:
            return redirect(translation.url)

        return super(TranslatablePageMixin, self).serve(request)


class BannerIndexPage(Page):
    parent_page_types = []
    subpage_types = ['BannerPage']


class BannerPage(TranslatablePageMixin, Page):
    parent_page_types = ['core.BannerIndexPage']
    subpage_types = []

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

BannerPage.content_panels = [
    FieldPanel('title', classname='full title'),
    ImageChooserPanel('banner'),
    PageChooserPanel('banner_link_page')
]


class Main(CommentedPageMixin, Page):
    parent_page_types = []
    subpage_types = []

    def bannerpages(self):
        return BannerPage.objects.live().filter(
            languages__language__is_main_language=True).specific()

    def sections(self):
        index_page = SectionIndexPage.objects.live().all().first()
        return SectionPage.objects.live().child_of(index_page).filter(
            languages__language__is_main_language=True).specific()

    def latest_articles(self):
        return ArticlePage.objects.live().filter(
            featured_in_latest=True,
            languages__language__is_main_language=True).order_by(
                '-latest_revision_created_at').specific()

    def footers(self):
        return FooterPage.objects.live().filter(
            languages__language__is_main_language=True).specific()


class LanguagePage(CommentedPageMixin, Page):
    code = models.CharField(
        max_length=255,
        help_text=_('The language code as specified in iso639-2'))

    parent_page_types = []
    subpage_types = []

    commenting_state = models.CharField(
        max_length=1,
        choices=constants.COMMENTING_STATE_CHOICES,
        blank=True,
        null=True)
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

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
    locale = models.CharField(
        verbose_name=_('language name'),
        choices=settings.LANGUAGES,
        max_length=255,
        blank=False,
        help_text=_("Site language")
    )
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

    def __str__(self):  # pragma: no cover
        return "%s" % (self.get_locale_display(),)

    class Meta:
        verbose_name = _('Language')


class SectionIndexPage(CommentedPageMixin, Page):
    parent_page_types = []
    subpage_types = ['SectionPage']

    commenting_state = models.CharField(
        max_length=1,
        choices=constants.COMMENTING_STATE_CHOICES,
        blank=True,
        null=True,
        default=constants.COMMENTING_OPEN)
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

SectionIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    MultiFieldPanel(
        [
            FieldPanel('commenting_state'),
            FieldPanel('commenting_open_time'),
            FieldPanel('commenting_close_time'),
        ],
        heading="Commenting Settings",)
]


class SectionPage(CommentedPageMixin, TranslatablePageMixin, Page):
    description = models.TextField(null=True, blank=True)
    uuid = models.CharField(max_length=32, blank=True, null=True)
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

    def articles(self):
        main_language_page = self.get_main_language_page()
        return ArticlePage.objects.live().child_of(main_language_page).filter(
            languages__language__is_main_language=True)

    def sections(self):
        main_language_page = self.get_main_language_page()
        return SectionPage.objects.live().child_of(main_language_page).filter(
            languages__language__is_main_language=True)

    def get_effective_extra_style_hints(self):
        if self.extra_style_hints:
            return self.extra_style_hints

        # The extra css is inherited from the parent SectionPage.
        # This will either return the current value or a value
        # from its parents.
        main_lang = SiteLanguage.objects.filter(is_main_language=True).first()
        language_rel = self.languages.all().first()
        if language_rel and main_lang == language_rel.language:
            parent_section = SectionPage.objects.all().ancestor_of(self).last()
            if parent_section:
                return parent_section.get_effective_extra_style_hints()
            return ''
        else:
            page = self.get_main_language_page()
            return page.specific.get_effective_extra_style_hints()

    def get_effective_image(self):
        if self.image:
            return self.image

        main_lang = SiteLanguage.objects.filter(is_main_language=True).first()
        language_rel = self.languages.all().first()
        if language_rel and main_lang == language_rel.language:
            parent_section = SectionPage.objects.all().ancestor_of(self).last()
            if parent_section:
                return parent_section.get_effective_image()
            return ''
        else:
            page = self.get_main_language_page()
            return page.specific.get_effective_image()

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


class ArticlePageTag(TaggedItemBase):
    content_object = ParentalKey(
        'core.ArticlePage', related_name='tagged_items')


class ArticlePageMetaDataTag(TaggedItemBase):
    content_object = ParentalKey(
        'core.ArticlePage', related_name='metadata_tagged_items')


class ArticlePage(CommentedPageMixin, TranslatablePageMixin, Page,
                  TagSearchable):
    subtitle = models.TextField(null=True, blank=True)
    uuid = models.CharField(max_length=32, blank=True, null=True)
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
    social_media_title = models.TextField(null=True, blank=True,
                                          verbose_name="title")
    social_media_description = models.TextField(null=True, blank=True,
                                                verbose_name="description")
    social_media_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        verbose_name="Image",
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
    metadata_tags = ClusterTaggableManager(
        through=ArticlePageMetaDataTag,
        blank=True, related_name="metadata_tags",
        help_text=_(
            'A comma-separated list of tags. '
            'This is not visible to the user.'))

    subpage_types = []
    search_fields = Page.search_fields + TagSearchable.search_fields + (
        index.SearchField('subtitle'),
        index.SearchField('body'),
        index.FilterField('locale'),
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

    metedata_promote_panels = [
        FieldPanel('metadata_tags'),
    ]

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
        heading="Commenting Settings",),
    MultiFieldPanel(
        [
            FieldPanel('social_media_title'),
            FieldPanel('social_media_description'),
            ImageChooserPanel('social_media_image'),
        ],
        heading="Social Media",)
]

ArticlePage.promote_panels = [
    MultiFieldPanel(ArticlePage.featured_promote_panels, "Featuring"),
    MultiFieldPanel(ArticlePage.metedata_promote_panels, "Metadata"),
    MultiFieldPanel(
        Page.promote_panels,
        "Common page configuration", "collapsible collapsed")]


class FooterIndexPage(Page):
    parent_page_types = []
    subpage_types = ['FooterPage']


class FooterPage(ArticlePage):
    parent_page_types = ['FooterIndexPage']
    subpage_types = []

FooterPage.content_panels = ArticlePage.content_panels
