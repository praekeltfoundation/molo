from django.contrib import admin
from django.core.urlresolvers import reverse
from molo.core.models import (
    ReactionQuestion, ReactionQuestionResponse, ArticlePage,
    ArticlePageLanguageProxy
)

from django.utils.html import format_html

from wagtail.contrib.modeladmin.options import (
    ModelAdmin as WagtailModelAdmin,
)
from wagtail.contrib.modeladmin.options import ModelAdminGroup
from wagtail.contrib.modeladmin.views import IndexView


class ReactionQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'live')
    fieldsets = (
        (
            None,
            {'fields': ('title', )}
        ),
    )
    readonly_fields = ['title']


class ReactionQuestionResponseAdmin(admin.ModelAdmin):
    list_display = ('question', 'choice', 'user', 'article')
    fieldsets = (
        (
            None,
            {'fields': ('question', 'choice', 'user', 'article')}
        ),
    )
    readonly_fields = ['question', 'choice']

admin.site.register(ReactionQuestion, ReactionQuestionAdmin)
admin.site.register(ReactionQuestionResponse, ReactionQuestionResponseAdmin)


class ReactionQuestionsModelAdmin(WagtailModelAdmin, ReactionQuestionAdmin):
    model = ReactionQuestion
    menu_label = 'Reaction Question'
    menu_icon = 'doc-full'
    add_to_settings_menu = False
    list_display = ('responses', 'live')

    def responses(self, obj, *args, **kwargs):
        url = reverse('reaction-question-results-admin', args=(obj.id,))
        return '<a href="%s">%s</a>' % (url, obj)

    def get_queryset(self, request):
        qs = super(ReactionQuestionAdmin, self).get_queryset(request)
        # Only show questions related to that site
        main = request.site.root_page
        return qs.descendant_of(main)

    responses.allow_tags = True
    responses.short_description = 'Title'


class ReactionQuestionsSummaryModelAdmin(
        WagtailModelAdmin, ReactionQuestionAdmin):
    model = ArticlePage
    menu_label = 'Reaction Question Summary'
    menu_icon = 'doc-full'
    add_to_settings_menu = False
    list_display = ('articles', 'live')

    def articles(self, obj, *args, **kwargs):
        url = reverse(
            'reaction-question-article-results-admin', args=(obj.id,))
        return '<a href="%s">%s</a>' % (url, obj)

    def get_queryset(self, request):
        qs = ArticlePage.objects.descendant_of(
            request.site.root_page).filter(
                languages__language__is_main_language=True)
        return qs
    articles.allow_tags = True
    articles.short_description = 'Title'


class ArticleModelAdminTemplate(IndexView):

    def get_template_names(self):
        return 'admin/model_admin_template.html'


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


class ArticleModelAdmin(WagtailModelAdmin, ArticleAdmin):
    model = ArticlePageLanguageProxy
    menu_label = 'Articles'
    menu_icon = 'doc-full-inverse'
    list_display = [
        'title', 'section', 'live', 'first_published_at', 'owner',
        'latest_revision_created_at',
        'featured_in_latest', 'featured_in_homepage', 'featured_in_section',
        'image_img'
    ]

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
                "<a href='{url}'>{section}</a>",
                section=obj.get_parent_section().get_admin_display_title(),
                url=obj.get_parent_section().url_path
            )

    section.short_description = 'Section'
    section.allow_tags = True

    def get_queryset(self, request):
        qs = ArticlePageLanguageProxy.objects.descendant_of(
            request.site.root_page)
        return qs


class AdminViewGroup(ModelAdminGroup):
    menu_label = 'Admin View'
    menu_icon = 'folder-open-inverse'
    menu_order = 1500
    items = (
        ArticleModelAdmin,
    )
