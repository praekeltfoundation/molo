from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.forms.utils import pretty_name
from django.utils.html import format_html
from wagtail.wagtailadmin.edit_handlers import EditHandler

from itertools import chain

from django.utils import timezone as django_timezone
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language_from_request
from django.shortcuts import redirect
from django.db.models.signals import (pre_save, post_save)
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
from wagtail.wagtailcore.models import PageManager
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.models import Image
from wagtail.contrib.wagtailroutablepage.models import route, RoutablePageMixin
from wagtailmedia.blocks import AbstractMediaChooserBlock
from wagtailmedia.models import AbstractMedia
from wagtail.wagtailcore.signals import page_unpublished

from molo.core.blocks import MarkDownBlock, SocialMediaLinkBlock
from molo.core import constants
from molo.core.api.constants import ERROR
from molo.core.forms import ArticlePageForm
from molo.core.utils import get_locale_code, generate_slug
from molo.core.mixins import PageEffectiveImageMixin
from molo.core.molo_wagtail_models import MoloPage
from molo.core.utils import (
    separate_fields,
    add_json_dump,
    add_list_of_things,
    attach_image,
    add_stream_fields,
    get_image_hash
)


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

    fb_analytics_app_id = models.CharField(
        verbose_name=_('Facebook Analytics App ID'),
        max_length=25,
        null=True,
        blank=True,
        help_text=_(
            "The tracking ID to be used to view Facebook Analytics")
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
    enable_service_directory = models.BooleanField(
        default=False, verbose_name='Enable service directory'
    )
    enable_multi_category_service_directory_search = models.BooleanField(
        default=False, verbose_name='Enable multi service directory search'
    )
    default_service_directory_radius = models.\
        PositiveSmallIntegerField(
            null=True,
            blank=True,
            verbose_name=_('Default Service Directory Radius'),
            help_text=_(
                'When set this will enable service directory radius filter '
                'as the set value for the default radius value'
            )
        )
    service_directory_api_base_url = models.CharField(
        verbose_name=_('service directory base url'),
        max_length=255,
        null=True,
        blank=True,
    )
    service_directory_api_username = models.CharField(
        verbose_name=_('service directory username'),
        max_length=255,
        null=True,
        blank=True,
    )
    service_directory_api_password = models.CharField(
        verbose_name=_('service directory password'),
        max_length=255,
        null=True,
        blank=True,
    )
    google_places_api_server_key = models.CharField(
        verbose_name=_('google places server key'),
        max_length=255,
        null=True,
        blank=True,
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
                FieldPanel('fb_analytics_app_id'),
            ],
            heading="Facebook Analytics Settings",
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
        ),
        MultiFieldPanel(
            [
                FieldPanel('enable_service_directory'),
                FieldPanel('service_directory_api_base_url'),
                FieldPanel('service_directory_api_username'),
                FieldPanel('service_directory_api_password'),
                FieldPanel('google_places_api_server_key'),
                FieldPanel('default_service_directory_radius'),
                FieldPanel('enable_multi_category_service_directory_search'),
            ],
            heading="Service Directory API Settings"
        )
    ]


class Timezone(models.Model):
    title = models.CharField(
        max_length=255,
        unique=True,
    )

    def __unicode__(self):
        return self.title


@register_setting
class CmsSettings(BaseSetting):
    '''
    CMS settings apply to every site running in this Django app. Wagtail
    settings are per-site, so this class applies the change to all sites when
    saving.
    '''

    timezone = models.ForeignKey(
        'core.Timezone',
        null=True,
        on_delete=models.PROTECT,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('timezone'),
            ],
            heading='Core settings',
        ),
    ]

    class Meta:
        verbose_name = 'CMS settings'

    def save(self, first_site_save=True, *args, **kwargs):
        super(CmsSettings, self).save(*args, **kwargs)

        if first_site_save:
            if self.timezone is not None:
                django_timezone.activate(self.timezone.title)

            for site in Site.objects.all():
                cms_settings = CmsSettings.for_site(site)
                cms_settings.timezone = self.timezone
                cms_settings.save(first_site_save=False)


class ImageInfo(models.Model):
    image_hash = models.CharField(max_length=256, null=True)
    image = models.OneToOneField(
        'wagtailimages.Image',
        null=True,
        blank=True,
        related_name='image_info'
    )

    def save(self, *args, **kwargs):
        self.image_hash = get_image_hash(self.image)
        super(ImageInfo, self).save(*args, **kwargs)


@receiver(
    post_save, sender=Image, dispatch_uid="create_image_info")
def create_image_info(sender, instance, **kwargs):
    image_info, created = ImageInfo.objects.get_or_create(image=instance)
    # ensure that image info is updated, in the event that an
    # image is changed e.g. file is changed, prompting change in hash
    if not created:
        image_info.save()


class ImportableMixin(object):
    @classmethod
    def create_page(self, content, class_, record_keeper=None, logger=None):
        '''
        Robust as possible

        Attempts to create the page
        If any of the functions used to attach content to the page
        fail, keep going, keep a record of those errors in a context dict
        return the page and the context dict in a tuple
        '''
        fields, nested_fields = separate_fields(content)

        foreign_id = content.pop('id')

        # remove unwanted fields
        if 'latest_revision_created_at' in content:
            content.pop('latest_revision_created_at')

        page = class_(**fields)

        # create functions to attach attributes
        function_args_mapping = (
            # add_section_time
            (add_json_dump, ("time", nested_fields, page)),
            # add_tags
            (add_list_of_things, ("tags", nested_fields, page)),
            # add_metadata_tags
            (add_list_of_things, ("metadata_tags", nested_fields, page)),

            # attach_image
            (attach_image, ("image", nested_fields, page, record_keeper)),
            # attach_social_media_image
            (attach_image, ("social_media_image", nested_fields,
                            page, record_keeper)),
            # attach_banner_image
            (attach_image, ("banner", nested_fields, page, record_keeper)),
        )

        for mapping in function_args_mapping:
            function = mapping[0]
            _args = mapping[1]
            try:
                function(*_args)
            except Exception as e:
                if logger:
                    logger.log(
                        ERROR,
                        "Failed to create page content",
                        {
                            "foreign_page_id": foreign_id,
                            "exception": e,
                            "function": function.__name__,
                        })

        # Handle content in nested_fields
        body = add_stream_fields(nested_fields, page)
        # body has not been added as it contains reference to pages
        if body:
            record_keeper.article_bodies[foreign_id] = body

        # Handle relationships in nested_fields
        if record_keeper:
            record_relation_functions = [
                record_keeper.record_nav_tags,
                record_keeper.record_recommended_articles,
                record_keeper.record_reaction_questions,
                record_keeper.record_related_sections,
                record_keeper.record_section_tags,
                record_keeper.record_banner_page_link,
            ]

            for function in record_relation_functions:
                try:
                    function(nested_fields, foreign_id)
                except Exception as e:
                    if logger:
                        logger.log(
                            ERROR,
                            "Failed to record content",
                            {
                                "foreign_page_id": foreign_id,
                                "exception": e,
                                "function": function.__name__,
                            })

        return page


class PreventDeleteMixin(object):
    hide_delete_button = True


class MoloMedia(AbstractMedia):
    youtube_link = models.CharField(max_length=512, null=True, blank=True)
    feature_in_homepage = models.BooleanField(default=False)

    admin_form_fields = (
        'title',
        'file',
        'collection',
        'duration',
        'width',
        'height',
        'thumbnail',
        'tags',
        'youtube_link',
        'feature_in_homepage',
    )


class MoloMediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context):
        if not value:
            return ''

        if value.type == 'video':
            player_code = '''
            <div>
                <video width="320" height="240" controls>
                    <source src="{0}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            '''
        else:
            player_code = '''
            <div>
                <audio controls>
                    <source src="{0}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            </div>
            '''
        return format_html(player_code, value.file.url)


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


def get_translation_for(pages, locale, site, is_live=True):
    show_only_translated_pages = SiteSettings.for_site(
        site).show_only_translated_pages
    language_setting = Languages.for_site(site)
    language = language_setting.languages.filter(
        locale=locale).first()

    if not language:
        if show_only_translated_pages:
            return []
        else:
            return list(pages)

    translated_pages = []
    for page in pages:
        cache_key = page.specific.get_translation_for_cache_key(
            locale, site, is_live)
        trans_pk = cache.get(cache_key)

    # TODO: consider pickling page object. Be careful about page size in
    # memory
        if trans_pk:
            translated_pages.append(Page.objects.get(pk=trans_pk).specific)
            continue
        main_language_page = page.specific.get_main_language_page()
        if language.is_main_language and not page == main_language_page:
            cache.set(cache_key, main_language_page.pk, None)
            translated_pages.append(main_language_page)
            continue

        # Filter the translation pages for this page by the given language
        try:
            translation = page.specific.translated_pages.get(
                language=language)
            if is_live is not None:
                if not translation.live:
                    translation = None
            if translation:
                translated = translation.specific
                cache.set(cache_key, translated.pk, None)
                translated_pages.append(translated)
            else:
                if not show_only_translated_pages:
                    translated_pages.append(page)
        except ObjectDoesNotExist:
            if not show_only_translated_pages:
                if is_live is not None:
                    if not page.live:
                        continue
                translated_pages.append(page)
            continue
    return translated_pages


class TranslatablePageMixinNotRoutable(object):
    def get_translation_for_cache_key(self, locale, site, is_live):
        return "get_translation_for_{}_{}_{}_{}_{}".format(
            self.pk, locale, site.pk, is_live,
            self.latest_revision_created_at.isoformat())

    def get_main_language_page(self):
        try:
            return self.translated_pages.get(
                language__is_main_language=True).specific
        except self.DoesNotExist:
            return self.specific

    def get_site(self):
        # TODO: this will need to change for one content repo work
        return self.get_ancestors().filter(
            depth=2).first().sites_rooted_here.all().first() or None

    def save(self, *args, **kwargs):
        response = super(
            TranslatablePageMixinNotRoutable, self).save(*args, **kwargs)
        languages = Languages.for_site(self.get_site()).languages
        if (languages.filter(
                is_main_language=True).exists() and
                not self.language):
            language = languages.filter(
                is_main_language=True).first()
            LanguageRelation.objects.create(
                page=self,
                language=language)
            self.language = language
            self.save()
        return response

    def move(self, target, pos=None):
        super(TranslatablePageMixinNotRoutable, self).move(target, pos)

        if hasattr(self, 'translated_pages'):
            for p in self.translated_pages.all():
                if not Page.objects.filter(pk=p.pk).first():
                    p.move(target, pos='last-child')

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
                page_copy.language = new_lang
                page_copy.save()
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
        main_lang = Languages.for_site(request.site).languages.filter(
            is_main_language=True).first()
        if main_lang.locale == locale_code:
            translation = parent
        else:
            translation = parent.specific.translated_pages.filter(
                language__locale=locale_code).first()

        if translation and self.language.locale != locale_code:
            if request.GET.urlencode():
                return redirect("{}?{}".format(translation.url,
                                               request.GET.urlencode()))
            else:
                return redirect(translation.url)

        return super(TranslatablePageMixinNotRoutable, self).serve(
            request, *args, **kwargs)


def clear_translation_cache(sender, instance, **kwargs):
    if isinstance(instance, TranslatablePageMixin):
        site = instance.get_site()
        for lang in Languages.for_site(site).languages.all():
            cache.delete(instance.get_translation_for_cache_key(
                lang.locale, site, True))
            cache.delete(instance.get_translation_for_cache_key(
                lang.locale, site, False))

            # clear cache for main language page too
            parent = instance.get_main_language_page()
            cache.delete(parent.get_translation_for_cache_key(
                lang.locale, site, True))
            cache.delete(parent.get_translation_for_cache_key(
                lang.locale, site, False))


page_unpublished.connect(clear_translation_cache)


class TranslatablePageMixin(
        TranslatablePageMixinNotRoutable, RoutablePageMixin):
    pass


class TagIndexPage(MoloPage, PreventDeleteMixin):
    parent_page_types = []
    subpage_types = ['Tag']

    def copy(self, *args, **kwargs):
        site = kwargs['to'].get_site()
        main = site.root_page
        TagIndexPage.objects.child_of(main).delete()
        super(TagIndexPage, self).copy(*args, **kwargs)


class ReactionQuestionIndexPage(MoloPage, PreventDeleteMixin):
    parent_page_types = []
    subpage_types = ['ReactionQuestion']

    def copy(self, *args, **kwargs):
        site = kwargs['to'].get_site()
        main = site.root_page
        ReactionQuestionIndexPage.objects.child_of(main).delete()
        super(ReactionQuestionIndexPage, self).copy(*args, **kwargs)


class ReactionQuestion(TranslatablePageMixin, MoloPage):
    parent_page_types = ['core.ReactionQuestionIndexPage']
    subpage_types = ['ReactionQuestionChoice']
    language = models.ForeignKey('core.SiteLanguage',
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 )
    translated_pages = models.ManyToManyField("self", blank=True)

    def has_user_submitted_reaction_response(
            self, request, reaction_id, article_id):
        if 'reaction_response_submissions' not in request.session:
            request.session['reaction_response_submissions'] = []
        if article_id in request.session['reaction_response_submissions']:
            return True
        return False


class ReactionQuestionChoice(TranslatablePageMixinNotRoutable,
                             PageEffectiveImageMixin, MoloPage):
    parent_page_types = ['core.ReactionQuestion']
    subpage_types = []
    language = models.ForeignKey('core.SiteLanguage',
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 )
    translated_pages = models.ManyToManyField("self", blank=True)

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

    class Meta:
        permissions = (
            ("can_view_response", "Can view Response"),
        )


class Tag(TranslatablePageMixin, MoloPage, ImportableMixin):
    parent_page_types = ['core.TagIndexPage']
    subpage_types = []
    language = models.ForeignKey('core.SiteLanguage',
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 )
    translated_pages = models.ManyToManyField("self", blank=True)
    feature_in_homepage = models.BooleanField(default=False)

    api_fields = [
        "id", "title", "feature_in_homepage", "go_live_at",
        "expire_at", "expired"
    ]


Tag.promote_panels = [
    FieldPanel('feature_in_homepage'),
    MultiFieldPanel(
        Page.promote_panels,
        "Common page configuration", "collapsible collapsed")
]


class BannerIndexPage(MoloPage, PreventDeleteMixin, ImportableMixin):
    parent_page_types = []
    subpage_types = ['BannerPage']

    def copy(self, *args, **kwargs):
        site = kwargs['to'].get_site()
        main = site.root_page
        BannerIndexPage.objects.child_of(main).delete()
        super(BannerIndexPage, self).copy(*args, **kwargs)


class BannerPage(ImportableMixin, TranslatablePageMixin, MoloPage):
    parent_page_types = ['core.BannerIndexPage']
    subpage_types = []
    language = models.ForeignKey('core.SiteLanguage',
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 )
    translated_pages = models.ManyToManyField("self", blank=True)

    subtitle = models.TextField(null=True, blank=True)
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
    api_fields = [
        "title", "subtitle", "banner", "banner_link_page", "external_link"]

    def get_effective_banner(self):
        if self.banner:
            return self.banner
        page = self.get_main_language_page()
        if page.specific.banner:
            return page.specific.get_effective_banner()
        return ''


BannerPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('subtitle'),
    ImageChooserPanel('banner'),
    PageChooserPanel('banner_link_page'),
    FieldPanel('external_link')
]

# Signal for allowing plugins to create indexes
index_pages_after_copy = Signal(providing_args=["instance"])


class Main(CommentedPageMixin, MoloPage):
    subpage_types = []

    def bannerpages(self):
        index_page = BannerIndexPage.objects.child_of(self).live().first()
        return BannerPage.objects.child_of(index_page).filter(
            language__is_main_language=True).specific()

    def sections(self):
        index_page = SectionIndexPage.objects.child_of(self).live().first()
        return SectionPage.objects.child_of(index_page).filter(
            language__is_main_language=True).specific()

    def latest_articles(self):
        return ArticlePage.objects.descendant_of(self).filter(
            featured_in_latest=True,
            language__is_main_language=True).exclude(
                feature_as_topic_of_the_day=True,
                demote_date__gt=django_timezone.now()).order_by(
                    '-featured_in_latest_start_date',
                    '-promote_date', '-latest_revision_created_at').specific()

    def topic_of_the_day(self):
        return ArticlePage.objects.descendant_of(self).filter(
            feature_as_topic_of_the_day=True,
            language__is_main_language=True,
            promote_date__lte=django_timezone.now(),
            demote_date__gte=django_timezone.now()).order_by(
            '-promote_date').specific()

    def footers(self):
        return FooterPage.objects.descendant_of(self).filter(
            language__is_main_language=True).specific()

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


class LanguagePage(CommentedPageMixin, MoloPage):
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

    api_fields = ["locale", "is_main_language", "is_active"]


class SiteLanguageRelation(Orderable, SiteLanguage):
    language_setting = ParentalKey(Languages, related_name='languages')


class SectionIndexPage(CommentedPageMixin, MoloPage, PreventDeleteMixin):
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


class SectionPage(ImportableMixin, CommentedPageMixin,
                  TranslatablePageMixin, MoloPage):
    language = models.ForeignKey('core.SiteLanguage',
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 )
    translated_pages = models.ManyToManyField("self", blank=True)
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

    api_fields = [
        "title", "live", "description", "image", "extra_style_hints",
        "commenting_state", "commenting_open_time",
        "commenting_close_time", "time", "monday_rotation",
        "tuesday_rotation", "wednesday_rotation", "thursday_rotation",
        "friday_rotation", "saturday_rotation", "sunday_rotation",
        "content_rotation_start_date", "content_rotation_end_date",
        "section_tags", "enable_next_section", "enable_recommended_section",
        "go_live_at", "expire_at", "expired"
    ]

    @classmethod
    def get_api_fields(cls):
        return cls.api_fields

    def articles(self):
        main_language_page = self.get_main_language_page()
        return list(chain(
            ArticlePage.objects.child_of(main_language_page).filter(
                language__is_main_language=True),
            ArticlePage.objects.filter(
                related_sections__section__slug=main_language_page.slug)))

    def sections(self):
        main_language_page = self.get_main_language_page()
        return SectionPage.objects.child_of(main_language_page).filter(
            language__is_main_language=True)

    def get_site(self):
        main = self.get_ancestors().filter(
            depth=2).first()
        return main.sites_rooted_here.all().first()

    def get_effective_extra_style_hints(self):
        cache_key = "effective_extra_style_hints_{}_{}".format(
            self.pk, self.latest_revision_created_at.isoformat())
        style = cache.get(cache_key)

        if style is not None:
            return style

        if self.extra_style_hints:
            return self.extra_style_hints

        # The extra css is inherited from the parent SectionPage.
        # This will either return the current value or a value
        # from its parents.
        main_lang = Languages.for_site(self.get_site()).languages.filter(
            is_main_language=True).first()

        language = self.language

        if not main_lang or not language:
            return ''

        if language and language.is_main_language is True:
            parent_section = SectionPage.objects.all().ancestor_of(self).last()
            if parent_section:
                style = parent_section.get_effective_extra_style_hints()
                cache.set(cache_key, style, 300)
                return style
            return ''
        else:
            page = self.get_main_language_page()
            style = page.specific.get_effective_extra_style_hints()
            cache.set(cache_key, style, 300)
            return style

    def get_effective_image(self):
        if self.image:
            return self.image

        main_lang = Languages.for_site(self.get_site()).languages.filter(
            is_main_language=True).first()
        if self.language and main_lang.pk == self.language.pk:
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
            language__is_main_language=True,
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


class ArticlePage(ImportableMixin, CommentedPageMixin,
                  TranslatablePageMixin, PageEffectiveImageMixin, MoloPage):
    language = models.ForeignKey('core.SiteLanguage',
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 )
    translated_pages = models.ManyToManyField("self", blank=True)
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
        ('media', MoloMediaBlock(icon='media'),)
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
            language = self.language
            if not destination_site.languages.languages.filter(
                    locale=language.locale).exists():
                new_lang = SiteLanguageRelation.objects.create(
                    language_setting=Languages.for_site(destination_site),
                    locale=language.locale,
                    is_active=False)
                self.language = new_lang
                self.save()
                LanguageRelation.objects.create(
                    page=self, language=new_lang)
        super(ArticlePage, self).move(*args, **kwargs)

    def get_absolute_url(self):  # pragma: no cover
        return self.url

    def get_parent_section(self):
        return self.get_parent().specific

    def allow_commenting(self):
        commenting_settings = self.get_effective_commenting_settings()
        if (commenting_settings['state'] != constants.COMMENTING_OPEN):
            now = django_timezone.now()
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
            now = django_timezone.now()
            return self.promote_date <= now <= self.demote_date
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
        ordering = ('-latest_revision_created_at',)

    api_fields = [
        "title", "subtitle", "body", "tags", "commenting_state",
        "commenting_open_time", "commenting_close_time", "social_media_title",
        "social_media_description", "social_media_image", "related_sections",
        "featured_in_latest", "featured_in_latest_start_date",
        "featured_in_latest_end_date", "featured_in_section",
        "featured_in_section_start_date", "featured_in_section_end_date",
        "featured_in_homepage", "featured_in_homepage_start_date",
        "featured_in_homepage_end_date", "feature_as_topic_of_the_day",
        "promote_date", "demote_date", "metadata_tags",
        "latest_revision_created_at", "image",
        "social_media_image", "social_media_description",
        "social_media_title", "reaction_questions",
        "nav_tags", "recommended_articles", "related_sections",
        "go_live_at", "expire_at", "expired"
    ]

    @classmethod
    def get_api_fields(cls):
        return cls.api_fields


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


class ArticlePageLanguageManager(PageManager):
    def get_queryset(self):
        return super(ArticlePageLanguageManager, self).get_queryset().filter(
            languages__language__is_main_language=True
        )


class ArticlePageLanguageProxy(ArticlePage):
    class Meta:
        proxy = True
        verbose_name = _('Article View')
        verbose_name_plural = _('Article View')

    objects = ArticlePageLanguageManager()

    @classmethod
    def get_indexed_objects(cls):
        '''
        Wagtail's ElasticSearch indexing adds all instances of
        a given model to the index which is causing duplicate
        articles in the search result.
        This get_indexed_objects method will exclude
        ArticlePageLanguageProxy items to be indexed
        '''
        return cls.objects.none()


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
    api_fields = ['tag']


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
    api_fields = ['tag']


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
    api_fields = ['reaction_question']


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
    api_fields = ['recommended_article']


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
    api_fields = ['section']


class FooterIndexPage(MoloPage, PreventDeleteMixin):
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
