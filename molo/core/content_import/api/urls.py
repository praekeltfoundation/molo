from django.conf.urls import url

from molo.core.content_import.api import admin_views


urlpatterns = [
    url(r"^import-articles/$", admin_views.ArticleImportView.as_view(), name="article-import"),
    url(r"^parent/$", admin_views.ArticleChooserView.as_view(model_admin=admin_views.ArticleModelAdmin()), name="test-parent"),
]