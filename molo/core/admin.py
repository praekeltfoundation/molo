from rangefilter.filter import DateRangeFilter
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.urls import reverse
from django.db.models import Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.modeladmin.options import (
    ModelAdmin as WagtailModelAdmin, modeladmin_register
)
from wagtail.contrib.modeladmin.options import ModelAdminGroup

from molo.core.models import (
    ArticlePage, ArticlePageLanguageProxy, SectionPage
)


class SectionPageAdmin(WagtailModelAdmin):
    model = SectionPage


modeladmin_register(SectionPageAdmin)


class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'live', 'first_published_at', 'owner',
        'latest_revision_created_at', 'go_live_at'
        'featured_in_latest', 'featured_in_homepage', 'featured_in_section'
    )

    fieldsets = (
        (
            None,
            {'fields': ('title', )}
        ),
    )
    readonly_fields = ['title']


class StatusCategoryListFilter(admin.SimpleListFilter):
    title = _('Status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('published', 'Published'),
            ('in_review', 'In Review'),
            ('draft', 'Draft')
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_review':
            return queryset.filter(revisions__submitted_for_moderation=True)
        elif self.value() == 'published':
            return queryset.filter(live=True)
        elif self.value() == 'draft':
            return queryset.filter(
                ~Q(revisions__submitted_for_moderation=True) & ~Q(live=True)
            )
        else:
            return queryset


class SectionListFilter(admin.SimpleListFilter):
    title = _('Sections')
    parameter_name = 'section'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        list_tuple = []
        for article in ArticlePage.objects.all():
            if article.get_parent_section():
                section_tuple = (
                    article.get_parent_section().id,
                    article.get_parent_section().title
                )
                if section_tuple not in list_tuple:
                    list_tuple.append(section_tuple)
        return list_tuple

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            try:
                section = SectionPage.objects.get(id=self.value())
                return queryset.child_of(section).all()
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                return None


class ArticlePageModelAdmin(WagtailModelAdmin, ArticleAdmin):
    model = ArticlePage


modeladmin_register(ArticlePageModelAdmin)


class ArticleModelAdmin(WagtailModelAdmin, ArticleAdmin):

    model = ArticlePageLanguageProxy
    menu_label = 'Articles'
    menu_icon = 'doc-full-inverse'
    list_display = [
        'article_title', 'section', 'live', 'status',
        'first_published_at', 'owner', 'first_created_at',
        'latest_revision_created_at', 'last_edited_by',
        'image_img', 'tags_html',
        'featured_in_latest', 'featured_in_homepage', 'featured_in_section',
    ]
    list_filter = [
        StatusCategoryListFilter,
        SectionListFilter,
        ('first_published_at', DateRangeFilter),
        ('latest_revision_created_at', DateRangeFilter),
        'featured_in_latest',
        'featured_in_homepage',
        'featured_in_section',
        'tags'
    ]
    search_fields = ('title', 'subtitle')

    def article_title(self, obj):
        return obj.title
    article_title.admin_order_field = 'title'
    article_title.short_description = 'Article Title'

    def image_img(self, obj):
        if obj.image:

            return u'<img src="%s" />' % (
                obj.image.get_rendition('height-50').url
            )

    image_img.short_description = 'Image'
    image_img.allow_tags = True

    def section(self, obj):
        if obj.get_parent_section():
            return format_html(
                "<a href='{section}'>{section_title}</a>",
                section_title=obj.get_parent_section(
                ).get_admin_display_title(),
                section=reverse(
                    'wagtailadmin_explore',
                    args=[obj.get_parent_section().id]
                )
            )

    section.short_description = 'Section'
    section.allow_tags = True

    def tags_html(self, obj):
        if obj.tags_list():
            display_value = ", ".join(obj.tags_list())
            result = display_value.upper()
            return result

    tags_html.short_description = 'Tags'
    tags_html.allow_tags = True

    def status(self, obj):
        if obj.get_latest_revision().submitted_for_moderation:
            return "In Review"
        elif obj.live:
            return "Published"
        else:
            return "Draft"

    status.short_description = 'Status'
    status.allow_tags = True

    def last_edited_by(self, obj):
        if obj.get_latest_revision():
            return obj.get_latest_revision().user

    last_edited_by.short_description = 'Last edited by'
    last_edited_by.allow_tags = True

    def first_created_at(self, obj):
        if obj.revisions.first():
            return obj.revisions.first().created_at

    first_created_at.short_description = 'Created at'
    first_created_at.allow_tags = True

    def get_queryset(self, request):
        qs = ArticlePageLanguageProxy.objects.descendant_of(
            request._wagtail_site.root_page)
        return qs


class AdminViewGroup(ModelAdminGroup):
    menu_label = 'Admin View'
    menu_icon = 'folder-open-inverse'
    menu_order = 1500
    items = (
        ArticleModelAdmin,
    )
