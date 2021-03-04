from molo.core.models import ArticlePage, SectionPage
from wagtail.contrib.modeladmin.options import (
    ModelAdmin as WagtailModelAdmin, modeladmin_register
)


class SectionPageAdmin(WagtailModelAdmin):
    model = SectionPage


modeladmin_register(SectionPageAdmin)


class ArticlePageModelAdmin(WagtailModelAdmin):
    model = ArticlePage


modeladmin_register(ArticlePageModelAdmin)
