from itertools import chain

from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language_from_request
from django.shortcuts import redirect
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver

from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, StreamFieldPanel, PageChooserPanel,
    MultiFieldPanel, InlinePanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock

from molo.core.blocks import MarkDownBlock, MultimediaBlock
from molo.core import constants, forms
from molo.core.utils import get_locale_code


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
        verbose_name=_('Local GA Tag Manager'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Local GA Tag Manager tracking code (e.g GTM-XXX) to be used to "
            "view analytics on this site only")
    )
    global_ga_tag_manager = models.CharField(
        verbose_name=_('Global GA Tag Manager'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Global GA Tag Manager tracking code (e.g GTM-XXX) to be used"
            " to view analytics on more than one site globally")
    )

    local_ga_tracking_code = models.CharField(
        verbose_name=_('Local GA Tracking Code'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Local GA tracking code to be used to "
            "view analytics on this site only")
    )
    global_ga_tracking_code = models.CharField(
        verbose_name=_('Global GA Tracking Code'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Global GA tracking code to be used"
            " to view analytics on more than one site globally")
    )
    show_only_translated_pages = models.BooleanField(
        default=False,
        help_text='When selecting this option, untranslated pages'
                  ' will not be visible to the front end user'
                  ' when they viewing a child language of the site')

    time = StreamField([
        ('time', blocks.TimeBlock(required=False)),
    ], null=True, blank=True, help_text='The time/s content will be rotated')

    monday_rotation = models.BooleanField(default=False, verbose_name='Monday')
    tuesday_rotation = models.BooleanField(
        default=False, verbose_name='Tuesday')
    wednesday_rotation = models.BooleanField(
        default=False, verbose_name='Wednesday')
    thursday_rotation = models.BooleanField(
        default=False, verbose_name='Thursday')
    friday_rotation = models.BooleanField(default=False, verbose_name='Friday')
    saturday_rotation = models.BooleanField(
        default=False, verbose_name='Saturday')
    sunday_rotation = models.BooleanField(default=False, verbose_name='Sunday')

    content_rotation_start_date = models.DateTimeField(
        null=True, blank=True,
        help_text='The date rotation will begin')
    content_rotation_end_date = models.DateTimeField(
        null=True, blank=True,
        help_text='The date rotation will end')

    panels = [
        ImageChooserPanel('logo'),
        MultiFieldPanel(
            [
                FieldPanel('show_only_translated_pages'),
            ],
            heading="Multi Language",
        ),
        MultiFieldPanel(
            [
                FieldPanel('ga_tag_manager'),
                FieldPanel('global_ga_tag_manager'),
            ],
            heading="GA Tag Manager Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel('local_ga_tracking_code'),
                FieldPanel('global_ga_tracking_code'),
            ],
            heading="GA Tracking Code Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel('content_rotation_start_date'),
                FieldPanel('content_rotation_end_date'),
                FieldRowPanel([
                    FieldPanel('monday_rotation', classname='col6'),
                    FieldPanel('tuesday_rotation', classname='col6'),
                    FieldPanel('wednesday_rotation', classname='col6'),
                    FieldPanel('thursday_rotation', classname='col6'),
                    FieldPanel('friday_rotation', classname='col6'),
                    FieldPanel('saturday_rotation', classname='col6'),
                    FieldPanel('sunday_rotation', classname='col6'),
                ]),
                StreamFieldPanel('time'),
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
        parent = self.get_main_language_page()
        translation = parent.specific.get_translation_for(locale_code)
        language_rel = self.languages.all().first()

        main_lang = SiteLanguage.objects.filter(is_main_language=True).first()
        if main_lang.locale == locale_code:
            translation = parent

        if translation and language_rel.language.locale != locale_code:
            return redirect(
                '%s?%s' % (translation.url, request.GET.urlencode()))

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
        return BannerPage.objects.filter(
            languages__language__is_main_language=True).specific()

    def sections(self):
        index_page = SectionIndexPage.objects.live().all().first()
        return SectionPage.objects.child_of(index_page).filter(
            languages__language__is_main_language=True).specific()

    def latest_articles(self):
        return ArticlePage.objects.filter(
            featured_in_latest=True,
            languages__language__is_main_language=True).exclude(
                feature_as_topic_of_the_day=True,
                demote_date__gt=timezone.now()).order_by(
                    '-promote_date', '-latest_revision_created_at').specific()

    def topic_of_the_day(self):
        return ArticlePage.objects.filter(
            feature_as_topic_of_the_day=True,
            languages__language__is_main_language=True,
            promote_date__lte=timezone.now(),
            demote_date__gte=timezone.now()).order_by(
            '-promote_date').specific()

    def footers(self):
        return FooterPage.objects.filter(
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

    time = StreamField([
        ('time', blocks.TimeBlock(required=False)),
    ], null=True, blank=True, help_text='The time/s content will be rotated')

    monday_rotation = models.BooleanField(default=False, verbose_name='Monday')
    tuesday_rotation = models.BooleanField(
        default=False, verbose_name='Tuesday')
    wednesday_rotation = models.BooleanField(
        default=False, verbose_name='Wednesday')
    thursday_rotation = models.BooleanField(
        default=False, verbose_name='Thursday')
    friday_rotation = models.BooleanField(default=False, verbose_name='Friday')
    saturday_rotation = models.BooleanField(
        default=False, verbose_name='Saturday')
    sunday_rotation = models.BooleanField(default=False, verbose_name='Sunday')

    content_rotation_start_date = models.DateTimeField(
        null=True, blank=True,
        help_text='The date rotation will begin')
    content_rotation_end_date = models.DateTimeField(
        null=True, blank=True,
        help_text='The date rotation will end')

    def articles(self):
        main_language_page = self.get_main_language_page()
        return list(chain(
            ArticlePage.objects.child_of(main_language_page).filter(
                languages__language__is_main_language=True),
            ArticlePage.objects.filter(
                related_sections__section__slug=main_language_page.slug)
        )
        )

    def sections(self):
        main_language_page = self.get_main_language_page()
        return SectionPage.objects.child_of(main_language_page).filter(
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

    def featured_in_homepage_articles(self):
        main_language_page = self.get_main_language_page()
        return ArticlePage.objects.child_of(main_language_page).filter(
            languages__language__is_main_language=True,
            featured_in_homepage=True).order_by(
                '-latest_revision_created_at').specific()

    def get_context(self, request):
        context = super(SectionPage, self).get_context(request)

        try:
            p = int(request.GET.get('p', 1))
        except ValueError:
            p = 1

        context['p'] = p
        return context

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
        [
            FieldPanel('content_rotation_start_date'),
            FieldPanel('content_rotation_end_date'),
            FieldRowPanel([
                FieldPanel('monday_rotation', classname='col6'),
                FieldPanel('tuesday_rotation', classname='col6'),
                FieldPanel('wednesday_rotation', classname='col6'),
                FieldPanel('thursday_rotation', classname='col6'),
                FieldPanel('friday_rotation', classname='col6'),
                FieldPanel('saturday_rotation', classname='col6'),
                FieldPanel('sunday_rotation', classname='col6'),
            ]),
            StreamFieldPanel('time'),
        ],
        heading="Content Rotation Settings",),
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


class ArticlePage(CommentedPageMixin, TranslatablePageMixin, Page):
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
        ('media', MultimediaBlock()),
    ], null=True, blank=True)

    tags = ClusterTaggableManager(through=ArticlePageTag, blank=True)
    metadata_tags = ClusterTaggableManager(
        through=ArticlePageMetaDataTag,
        blank=True, related_name="metadata_tags",
        help_text=_(
            'A comma-separated list of tags. '
            'This is not visible to the user.'))

    subpage_types = []
    search_fields = Page.search_fields + (
        index.SearchField('subtitle'),
        index.SearchField('body'),
        index.RelatedFields('tags', [
            index.SearchField('name', partial_match=True, boost=2),
        ]),
    )

    commenting_state = models.CharField(
        max_length=1,
        choices=constants.COMMENTING_STATE_CHOICES,
        blank=True,
        null=True)
    commenting_open_time = models.DateTimeField(null=True, blank=True)
    commenting_close_time = models.DateTimeField(null=True, blank=True)

    feature_as_topic_of_the_day = models.BooleanField(
        default=False,
        help_text=_('Article to be featured as the Topic of the Day'))
    promote_date = models.DateTimeField(blank=True, null=True)
    demote_date = models.DateTimeField(blank=True, null=True)

    featured_promote_panels = [
        FieldPanel('featured_in_latest'),
        FieldPanel('featured_in_section'),
        FieldPanel('featured_in_homepage'),
    ]

    topic_of_the_day_panels = [
        FieldPanel('feature_as_topic_of_the_day'),
        FieldPanel('promote_date'),
        FieldPanel('demote_date'),
    ]

    metedata_promote_panels = [
        FieldPanel('metadata_tags'),
    ]

    base_form_class = forms.ArticlePageForm

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

    def is_current_topic_of_the_day(self):
        if self.feature_as_topic_of_the_day:
            return self.promote_date <= timezone.now() <= self.demote_date
        return False

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
        heading="Social Media",),
    InlinePanel('related_sections', label="Related Sections"),
]

ArticlePage.promote_panels = [
    MultiFieldPanel(ArticlePage.featured_promote_panels, "Featuring"),
    MultiFieldPanel(ArticlePage.topic_of_the_day_panels, "Topic of the Day"),
    MultiFieldPanel(ArticlePage.metedata_promote_panels, "Metadata"),
    MultiFieldPanel(
        Page.promote_panels,
        "Common page configuration", "collapsible collapsed")]


class ArticlePageRelatedSections(Orderable):
    page = ParentalKey(ArticlePage, related_name='related_sections')
    section = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Section that this page also belongs too')
    )
    panels = [PageChooserPanel('section', 'core.SectionPage')]


class FooterIndexPage(Page):
    parent_page_types = []
    subpage_types = ['FooterPage']


class FooterPage(ArticlePage):
    parent_page_types = ['FooterIndexPage']
    subpage_types = []

FooterPage.content_panels = ArticlePage.content_panels

pages_to_delete = []


@receiver(pre_delete, sender=Page)
def on_page_delete(sender, instance, *a, **kw):
    ids = PageTranslation.objects.filter(
        page=instance).values_list('translated_page__id')
    pages_to_delete.extend(Page.objects.filter(id__in=ids))


@receiver(post_delete, sender=Page)
def on_post_page_delete(sender, instance, *a, **kw):
    # When we try to delete a translated page in our pre_delete, wagtail
    # pre_delete function would want to get the same page too, but since we
    # have already deleted it, wagtail would not be able to find it, therefore
    # we have to get the translated page in our pre_delete and use a global
    # variable to store it and pass it into the post_delete and remove it here
    for p in pages_to_delete:
        p.delete()

    global pages_to_delete
    del pages_to_delete[:]
