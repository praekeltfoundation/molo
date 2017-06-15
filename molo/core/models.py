from django.forms.utils import pretty_name
from django.utils.html import format_html
from wagtail.wagtailadmin.edit_handlers import EditHandler

from itertools import chain

from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language_from_request
from django.shortcuts import redirect
from django.db.models.signals import (
    pre_delete, post_delete, pre_save, post_save)
from django.dispatch import receiver, Signal
from django.template.response import TemplateResponse

from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from modelcluster.models import ClusterableModel

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailcore.models import Page, Orderable, Site
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, StreamFieldPanel, PageChooserPanel,
    MultiFieldPanel, InlinePanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.contrib.wagtailroutablepage.models import route, RoutablePageMixin

from molo.core.blocks import MarkDownBlock, MultimediaBlock, \
    SocialMediaLinkBlock
from molo.core import constants
from molo.core.forms import ArticlePageForm
from molo.core.utils import get_locale_code, generate_slug
from molo.core.mixins import PageEffectiveImageMixin


class BaseReadOnlyPanel(EditHandler):
    def render(self):
        value = getattr(self.instance, self.attr)
        if callable(value):
            value = value()
        return format_html('<div style="padding-top: 1.2em;">{}</div>', value)

    def render_as_object(self):
        return format_html(
            '<fieldset><legend>{}</legend>'
            '<ul class="fields"><li><div class="field">{}</div></li></ul>'
            '</fieldset>',
            self.heading, self.render())

    def render_as_field(self):
        return format_html(
            '<div class="field">'
            '<label>{}{}</label>'
            '<div class="field-content">{}</div>'
            '</div>',
            self.heading, _(':'), self.render())


class ReadOnlyPanel:
    def __init__(self, attr, heading=None, classname=''):
        self.attr = attr
        self.heading = pretty_name(self.attr) if heading is None else heading
        self.classname = classname

    def bind_to_model(self, model):
        return type(str(_('ReadOnlyPanel')), (BaseReadOnlyPanel,),
                    {'attr': self.attr, 'heading': self.heading,
                     'classname': self.classname})


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

    social_media_links_on_footer_page = StreamField([
        ('social_media_site', SocialMediaLinkBlock()),
    ], null=True, blank=True)
    facebook_sharing = models.BooleanField(
        default=False, verbose_name='Facebook',
        help_text='Enable this field to allow for sharing to Facebook.')
    facebook_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    twitter_sharing = models.BooleanField(
        default=False, verbose_name='Twitter',
        help_text='Enable this field to allow for sharing to Twitter.')
    twitter_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    enable_clickable_tags = models.BooleanField(
        default=False, verbose_name='Display tags on Front-end')
    enable_tag_navigation = models.BooleanField(
        default=False,
        help_text='Enable tag navigation. When this is true, the clickable '
                  'tag functionality will be overriden'
    )

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
            heading="Content Rotation Settings", ),
        MultiFieldPanel(
            [
                MultiFieldPanel(
                    [
                        StreamFieldPanel('social_media_links_on_footer_page'),
                    ],
                    heading="Social Media Footer Page", ),
            ],
            heading="Social Media Footer Page Links", ),
        MultiFieldPanel(
            [
                FieldPanel('facebook_sharing'),
                ImageChooserPanel('facebook_image'),
                FieldPanel('twitter_sharing'),
                ImageChooserPanel('twitter_image'),
            ],
            heading="Social Media Article Sharing Buttons",
        ),
        MultiFieldPanel(
            [
                FieldPanel('enable_clickable_tags'),
                FieldPanel('enable_tag_navigation'),
            ],
            heading="Article Tag Settings"
        )
    ]


class PreventDeleteMixin(object):
    hide_delete_button = True


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


class TranslatablePageMixinNotRoutable(object):
    def get_translation_for(self, locale, site, is_live=True):
        language_setting = Languages.for_site(site)
        language = language_setting.languages.filter(
            locale=locale).first()

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
            return self.specific.source_page.page.specific
        return self.specific

    def get_site(self):
        return self.get_ancestors().filter(
            depth=2).first().sites_rooted_here.all().first() or None

    def save(self, *args, **kwargs):
        response = super(
            TranslatablePageMixinNotRoutable, self).save(*args, **kwargs)
        languages = Languages.for_site(self.get_site()).languages
        if (languages.filter(
                is_main_language=True).exists() and
                not self.languages.exists()):
            LanguageRelation.objects.create(
                page=self,
                language=languages.filter(
                    is_main_language=True).first())
        return response

    def move(self, target, pos=None):
        super(TranslatablePageMixinNotRoutable, self).move(target, pos)

        if hasattr(self, 'translations'):
            for p in self.translations.all():
                p.translated_page.move(target, pos='last-child')

    def copy_language(self, current_site, destination_site):
        language = self.languages.all().first()
        if language:
            if not hasattr(destination_site, 'languages') or \
                not destination_site.languages.languages.filter(
                    locale=language.language.locale).exists():
                new_lang = SiteLanguageRelation.objects.create(
                    language_setting=Languages.for_site(destination_site),
                    locale=language.language.locale,
                    is_active=False)
            else:
                new_lang = destination_site.languages.languages.filter(
                    locale=language.language.locale).first()
            return new_lang

    def copy(self, *args, **kwargs):
        current_site = self.get_site()
        destination_site = kwargs['to'].get_site()
        if current_site is not destination_site:
            new_lang = self.copy_language(current_site, destination_site)
            page_copy = super(TranslatablePageMixinNotRoutable, self).copy(
                *args, **kwargs)

            if new_lang:
                new_l_rel, _ = LanguageRelation.objects.get_or_create(
                    page=page_copy)
                new_l_rel.language = new_lang
                new_l_rel.save()

            old_parent = self.get_main_language_page()
            if old_parent:
                new_translation_parent = \
                    page_copy.get_parent().get_children().filter(
                        slug=old_parent.slug).first()
                if new_translation_parent:
                    PageTranslation.objects.create(
                        page=new_translation_parent,
                        translated_page=page_copy)
            return page_copy
        else:
            return super(TranslatablePageMixinNotRoutable, self).copy(
                *args, **kwargs)

    @route(r'^noredirect/$')
    def noredirect(self, request):
        return Page.serve(self, request)

    @route(r'^$')
    def main(self, request):
        return TemplateResponse(
            request, self.get_template(request),
            self.get_context(request))

    def get_sitemap_urls(self):
        return [
            {
                'location': self.full_url,
                'lastmod': self.latest_revision_created_at
            }
        ]

    def serve(self, request, *args, **kwargs):
        locale_code = get_locale_code(get_language_from_request(request))
        parent = self.get_main_language_page()
        translation = parent.specific.get_translation_for(
            locale_code, request.site)
        language_rel = self.languages.all().first()

        main_lang = Languages.for_site(request.site).languages.filter(
            is_main_language=True).first()
        if main_lang.locale == locale_code:
            translation = parent

        path_components = [
            component for component in request.path.split('/') if component]
        if path_components and path_components[-1] != 'noredirect' and \
                translation and language_rel.language.locale != locale_code:
            return redirect(
                '%s?%s' % (translation.url, request.GET.urlencode()))

        return super(TranslatablePageMixinNotRoutable, self).serve(
            request, *args, **kwargs)


class TranslatablePageMixin(
        TranslatablePageMixinNotRoutable, RoutablePageMixin):
    pass


class TagIndexPage(Page, PreventDeleteMixin):
    parent_page_types = []
    subpage_types = ['Tag']

    def copy(self, *args, **kwargs):
        site = kwargs['to'].get_site()
        main = site.root_page
        TagIndexPage.objects.child_of(main).delete()
        super(TagIndexPage, self).copy(*args, **kwargs)


class ReactionQuestionIndexPage(Page, PreventDeleteMixin):
    parent_page_types = []
    subpage_types = ['ReactionQuestion']

    def copy(self, *args, **kwargs):
        site = kwargs['to'].get_site()
        main = site.root_page
        ReactionQuestionIndexPage.objects.child_of(main).delete()
        super(ReactionQuestionIndexPage, self).copy(*args, **kwargs)


class ReactionQuestion(TranslatablePageMixin, Page):
    parent_page_types = ['core.ReactionQuestionIndexPage']
    subpage_types = ['ReactionQuestionChoice']

    def has_user_submitted_reaction_response(
            self, request, reaction_id, article_id):
        if 'reaction_response_submissions' not in request.session:
            request.session['reaction_response_submissions'] = []
        if article_id in request.session['reaction_response_submissions']:
            return True
        return False


class ReactionQuestionChoice(
        TranslatablePageMixinNotRoutable, PageEffectiveImageMixin, Page):
    parent_page_types = ['core.ReactionQuestion']
    subpage_types = []

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    success_message = models.CharField(blank=True, null=True, max_length=1000)
    success_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

ReactionQuestionChoice.content_panels = [
    FieldPanel('title', classname='full title'),
    ImageChooserPanel('image'),
    FieldPanel('success_message', classname='full title'),
    ImageChooserPanel('success_image'),
]


class ReactionQuestionResponse(models.Model):
    user = models.ForeignKey('auth.User', blank=True, null=True)
    article = models.ForeignKey('core.ArticlePage')
    choice = models.ForeignKey(
        'core.ReactionQuestionChoice', blank=True, null=True)
    question = models.ForeignKey('core.ReactionQuestion')
    created_at = models.DateTimeField(auto_now_add=True)

    def set_response_as_submitted_for_session(self, request, article):
        if 'reaction_response_submissions' not in request.session:
            request.session['reaction_response_submissions'] = []
        request.session['reaction_response_submissions'].append(article.id)
        request.session.modified = True


class Tag(TranslatablePageMixin, Page):
    parent_page_types = ['core.TagIndexPage']
    subpage_types = []

    feature_in_homepage = models.BooleanField(default=False)


Tag.promote_panels = [
    FieldPanel('feature_in_homepage'),
    MultiFieldPanel(
        Page.promote_panels,
        "Common page configuration", "collapsible collapsed")
]


class BannerIndexPage(Page, PreventDeleteMixin):
    parent_page_types = []
    subpage_types = ['BannerPage']

    def copy(self, *args, **kwargs):
        site = kwargs['to'].get_site()
        main = site.root_page
        BannerIndexPage.objects.child_of(main).delete()
        super(BannerIndexPage, self).copy(*args, **kwargs)


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
    external_link = models.TextField(null=True, blank=True,
                                     help_text='External link which a banner'
                                     ' will link to. '
                                     'eg https://www.google.co.za/')


BannerPage.content_panels = [
    FieldPanel('title', classname='full title'),
    ImageChooserPanel('banner'),
    PageChooserPanel('banner_link_page'),
    FieldPanel('external_link')
]

# Signal for allowing plugins to create indexes
index_pages_after_copy = Signal(providing_args=["instance"])


class Main(CommentedPageMixin, Page):
    subpage_types = []

    def bannerpages(self):
        index_page = BannerIndexPage.objects.child_of(self).live().first()
        return BannerPage.objects.child_of(index_page).filter(
            languages__language__is_main_language=True).specific()

    def sections(self):
        index_page = SectionIndexPage.objects.child_of(self).live().first()
        return SectionPage.objects.child_of(index_page).filter(
            languages__language__is_main_language=True).specific()

    def latest_articles(self):
        return ArticlePage.objects.descendant_of(self).filter(
            featured_in_latest=True,
            languages__language__is_main_language=True).exclude(
                feature_as_topic_of_the_day=True,
                demote_date__gt=timezone.now()).order_by(
                    '-featured_in_latest_start_date',
                    '-promote_date', '-latest_revision_created_at').specific()

    def topic_of_the_day(self):
        return ArticlePage.objects.descendant_of(self).filter(
            feature_as_topic_of_the_day=True,
            languages__language__is_main_language=True,
            promote_date__lte=timezone.now(),
            demote_date__gte=timezone.now()).order_by(
            '-promote_date').specific()

    def footers(self):
        return FooterPage.objects.descendant_of(self).filter(
            languages__language__is_main_language=True).specific()

    def save(self, *args, **kwargs):
        super(Main, self).save(*args, **kwargs)
        if not self.get_descendants().exists():
            banner_index = BannerIndexPage(
                title='Banners', slug=('banners-%s' % (
                    generate_slug(self.title), )))
            self.add_child(instance=banner_index)
            banner_index.save_revision().publish()
            section_index = SectionIndexPage(
                title='Sections', slug=('sections-%s' % (
                    generate_slug(self.title), )))
            self.add_child(instance=section_index)
            section_index.save_revision().publish()
            footer_index = FooterIndexPage(
                title='Footers', slug=('footers-%s' % (
                    generate_slug(self.title), )))
            self.add_child(instance=footer_index)
            footer_index.save_revision().publish()
            tag_index = TagIndexPage(
                title='Tags', slug=('tags-%s' % (
                    generate_slug(self.title), )))
            self.add_child(instance=tag_index)
            tag_index.save_revision().publish()
            reaction_question_index = ReactionQuestionIndexPage(
                title='Reaction Questions', slug=('reaction-questions-%s' % (
                    generate_slug(self.title), )))
            self.add_child(instance=reaction_question_index)
            reaction_question_index.save_revision().publish()
            index_pages_after_copy.send(sender=self.__class__, instance=self)


@receiver(
    post_save, sender=Main, dispatch_uid="create_site")
def create_site(sender, instance, **kwargs):
    default_site = not(Site.objects.all().exists())

    if not hasattr(settings, 'DEFAULT_SITE_PORT'):
        port = 80
    else:
        port = settings.DEFAULT_SITE_PORT
    # create site
    if not instance.sites_rooted_here.exists():
        site = Site(
            hostname=generate_slug(instance.title) + '.localhost',
            port=port, root_page=instance,
            is_default_site=default_site)
        site.save()


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
        heading="Commenting Settings", )
]


@register_setting
class Languages(BaseSetting, ClusterableModel):

    panels = [
        InlinePanel('languages', label="Site Languages"),
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
        if Languages.for_site(self.language_setting.site).languages.filter(
                is_main_language=True).exists():
            return super(SiteLanguage, self).save(*args, **kwargs)

        self.is_main_language = True
        return super(SiteLanguage, self).save(*args, **kwargs)

    def __str__(self):  # pragma: no cover
        return "%s" % (self.get_locale_display(),)

    class Meta:
        verbose_name = _('Language')

    panels = [
        FieldPanel('locale'),
        FieldPanel('is_active'),
        ReadOnlyPanel('is_main_language')
    ]


class SiteLanguageRelation(Orderable, SiteLanguage):
    language_setting = ParentalKey(Languages, related_name='languages')


class SectionIndexPage(CommentedPageMixin, Page, PreventDeleteMixin):
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

    def celery_copy(self, *args, **kwargs):
        SectionIndexPage.objects.child_of(kwargs['to']).delete()
        return super(SectionIndexPage, self).copy(*args, **kwargs)

    def copy(self, *args, **kwargs):
        from molo.core.tasks import copy_sections_index

        via_celery = kwargs.get('via_celery')

        if via_celery:
            del kwargs['via_celery']
            return self.celery_copy(*args, **kwargs)

        user = kwargs.get('user')
        user_pk = user.pk if user else None
        to_pk = kwargs['to'].pk
        copy_revisions = kwargs.get('copy_revisions')
        recursive = kwargs.get('recursive')
        keep_live = kwargs.get('keep_live')

        # workaround for celery tasks
        # https://github.com/celery/django-celery/issues/201
        if hasattr(settings, 'CELERY_ALWAYS_EAGER') and \
                settings.CELERY_ALWAYS_EAGER and settings.DEBUG:
            copy_sections_index(
                self.pk, user_pk, to_pk, copy_revisions, recursive, keep_live)
        else:
            copy_sections_index.delay(
                self.pk, user_pk, to_pk, copy_revisions, recursive, keep_live)


SectionIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    MultiFieldPanel(
        [
            FieldPanel('commenting_state'),
            FieldPanel('commenting_open_time'),
            FieldPanel('commenting_close_time'),
        ],
        heading="Commenting Settings", )
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
    parent_page_types = ['core.SectionIndexPage', 'core.SectionPage']
    subpage_types = ['core.ArticlePage', 'core.SectionPage']
    search_fields = Page.search_fields + [
        index.SearchField('description'),
    ]
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

    enable_next_section = (
        models.BooleanField(
            default=False,
            verbose_name='Activate up next section underneath articles',
            help_text=("Activate up next section underneath articles in this "
                       "section will appear with the heading and subheading of"
                       " that article. The text will say 'next' in order to "
                       "make the user feel like it's fresh content.")))
    enable_recommended_section = (
        models.BooleanField(
            default=False,
            verbose_name='Activate recommended section underneath articles',
            help_text=("Underneath the area for 'next articles' recommended "
                       "articles will appear, with the image + heading + "
                       "subheading")))

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

    def get_site(self):
        main = self.get_ancestors().filter(
            depth=2).first()
        return main.sites_rooted_here.all().first()

    def get_effective_extra_style_hints(self):
        if self.extra_style_hints:
            return self.extra_style_hints

        # The extra css is inherited from the parent SectionPage.
        # This will either return the current value or a value
        # from its parents.
        main_lang = Languages.for_site(self.get_site()).languages.filter(
            is_main_language=True).first()

        language_rel = self.languages.all().first()

        if not main_lang or not language_rel:
            return ''

        if language_rel and main_lang.pk == language_rel.language.pk:
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

        main_lang = Languages.for_site(self.get_site()).languages.filter(
            is_main_language=True).first()
        language_rel = self.languages.all().first()
        if language_rel and main_lang.pk == language_rel.language.pk:
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
        heading="Commenting Settings", ),
    InlinePanel('section_tags', label="Tags for Navigation"),
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
        heading="Content Rotation Settings", ),
    MultiFieldPanel(
        [FieldRowPanel(
            [FieldPanel('extra_style_hints')], classname="label-above")],
        "Meta"),
    MultiFieldPanel(
        [
            FieldPanel('enable_next_section'),
            FieldPanel('enable_recommended_section')
        ],
        heading="Recommended Settings", )
]


class ArticlePageTag(TaggedItemBase):
    content_object = ParentalKey(
        'core.ArticlePage', related_name='tagged_items')


class ArticlePageMetaDataTag(TaggedItemBase):
    content_object = ParentalKey(
        'core.ArticlePage', related_name='metadata_tagged_items')


class ArticlePage(
        CommentedPageMixin, TranslatablePageMixin, PageEffectiveImageMixin,
        Page):
    parent_page_types = ['core.SectionPage']

    subtitle = models.TextField(null=True, blank=True)
    uuid = models.CharField(max_length=32, blank=True, null=True)
    featured_in_latest = models.BooleanField(
        default=False,
        help_text=_("Article to be featured in the Latest module"))
    featured_in_latest_start_date = models.DateTimeField(null=True, blank=True)
    featured_in_latest_end_date = models.DateTimeField(null=True, blank=True)
    featured_in_section = models.BooleanField(
        default=False,
        help_text=_("Article to be featured in the Section module"))
    featured_in_section_start_date = models.DateTimeField(
        null=True, blank=True)
    featured_in_section_end_date = models.DateTimeField(null=True, blank=True)
    featured_in_homepage = models.BooleanField(
        default=False,
        help_text=_(
            "Article to be featured in the Homepage "
            "within the Section module"))
    featured_in_homepage_start_date = models.DateTimeField(
        null=True, blank=True)
    featured_in_homepage_end_date = models.DateTimeField(null=True, blank=True)
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
    search_fields = Page.search_fields + [
        index.SearchField('subtitle'),
        index.SearchField('body'),
        index.RelatedFields('tags', [
            index.SearchField('name', partial_match=True, boost=2),
        ]),
    ]

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

    featured_latest_promote_panels = [
        FieldPanel('featured_in_latest_start_date'),
        FieldPanel('featured_in_latest_end_date'),
    ]
    featured_section_promote_panels = [
        FieldPanel('featured_in_section_start_date'),
        FieldPanel('featured_in_section_end_date'),

    ]
    featured_homepage_promote_panels = [
        FieldPanel('featured_in_homepage_start_date'),
        FieldPanel('featured_in_homepage_end_date'),
    ]

    topic_of_the_day_panels = [
        FieldPanel('feature_as_topic_of_the_day'),
        FieldPanel('promote_date'),
        FieldPanel('demote_date'),
    ]

    metedata_promote_panels = [
        FieldPanel('metadata_tags'),
    ]

    base_form_class = ArticlePageForm

    def move(self, *args, **kwargs):
        current_site = self.get_site()
        destination_site = args[0].get_site()

        if not (current_site is destination_site):
            for language in self.languages.all():
                if not destination_site.languages.languages.filter(
                        locale=language.language.locale).exists():
                    new_lang = SiteLanguageRelation.objects.create(
                        language_setting=Languages.for_site(destination_site),
                        locale=language.language.locale,
                        is_active=False)
                    LanguageRelation.objects.create(
                        page=self, language=new_lang)
        super(ArticlePage, self).move(*args, **kwargs)

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

    def tags_list(self):
        return self.tags.names()

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
        heading="Commenting Settings", ),
    MultiFieldPanel(
        [
            FieldPanel('social_media_title'),
            FieldPanel('social_media_description'),
            ImageChooserPanel('social_media_image'),
        ],
        heading="Social Media", ),
    InlinePanel('nav_tags', label="Tags for Navigation"),
    InlinePanel('reaction_questions', label="Reaction Questions"),
    InlinePanel('recommended_articles', label="Recommended articles"),
    InlinePanel('related_sections', label="Related Sections"),
]

ArticlePage.promote_panels = [
    MultiFieldPanel(
        ArticlePage.featured_latest_promote_panels, "Featuring in Latest"),
    MultiFieldPanel(
        ArticlePage.featured_section_promote_panels, "Featuring in Section"),
    MultiFieldPanel(
        ArticlePage.featured_homepage_promote_panels, "Featuring in Homepage"),
    MultiFieldPanel(ArticlePage.topic_of_the_day_panels, "Topic of the Day"),
    MultiFieldPanel(ArticlePage.metedata_promote_panels, "Metadata"),
    MultiFieldPanel(
        Page.promote_panels,
        "Common page configuration", "collapsible collapsed")]


@receiver(
    pre_save, sender=ArticlePage, dispatch_uid="demote_featured_articles")
def demote_featured_articles(sender, instance, **kwargs):
    if instance.featured_in_latest_end_date is None and \
        instance.featured_in_latest_start_date is None and \
            instance.featured_in_latest is True:
        instance.featured_in_latest = False
    if instance.featured_in_homepage_end_date is None and \
        instance.featured_in_homepage_start_date is None and \
            instance.featured_in_homepage is True:
        instance.featured_in_homepage = False
    if instance.featured_in_section_end_date is None and \
        instance.featured_in_section_start_date is None and \
            instance.featured_in_section is True:
        instance.featured_in_section = False


class SectionPageTags(Orderable):
    page = ParentalKey(SectionPage, related_name='section_tags')
    tag = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Tags for tag navigation')
    )
    panels = [PageChooserPanel('tag', 'core.Tag')]


class ArticlePageTags(Orderable):
    page = ParentalKey(ArticlePage, related_name='nav_tags')
    tag = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Tags for tag navigation')
    )
    panels = [PageChooserPanel('tag', 'core.Tag')]


class ArticlePageReactionQuestions(Orderable):
    page = ParentalKey(ArticlePage, related_name='reaction_questions')
    reaction_question = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Reaction Questions')
    )
    panels = [PageChooserPanel('reaction_question', 'core.ReactionQuestion')]


class ArticlePageRecommendedSections(Orderable):
    page = ParentalKey(ArticlePage, related_name='recommended_articles')
    recommended_article = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Recommended articles for this article')
    )
    panels = [PageChooserPanel('recommended_article', 'core.ArticlePage')]


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


class FooterIndexPage(Page, PreventDeleteMixin):
    parent_page_types = []
    subpage_types = ['FooterPage']

    def copy(self, *args, **kwargs):
        site = kwargs['to'].get_site()
        main = site.root_page
        FooterIndexPage.objects.child_of(main).delete()
        super(FooterIndexPage, self).copy(*args, **kwargs)


class FooterPage(ArticlePage):
    parent_page_types = ['FooterIndexPage']
    subpage_types = []


FooterPage.content_panels = ArticlePage.content_panels
FooterPage.promote_panels = [
    MultiFieldPanel(
        Page.promote_panels,
        "Common page configuration", "collapsible collapsed")]


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
