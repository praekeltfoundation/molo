from django.conf.urls import re_path

from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.documents.api.v2.views import DocumentsAPIViewSet


from molo.core.api import admin_views
from molo.core.api.endpoints import (
    MoloImagesAPIEndpoint,
    MoloPagesEndpoint,
    LanguagesAPIEndpoint,
)

# Adding extended images endpoint to new router.
# For consistency, the "pages" and "documents"
# endpoints have also been added even though they were
# not modified.
api_router = WagtailAPIRouter("wagtailapi_v2")
api_router.register_endpoint("images", MoloImagesAPIEndpoint)
api_router.register_endpoint("pages", MoloPagesEndpoint)
api_router.register_endpoint("documents", DocumentsAPIViewSet)
api_router.register_endpoint("languages", LanguagesAPIEndpoint)

urlpatterns = [
    re_path(
        r"^import-site/$",
        admin_views.SiteImportView.as_view(),
        name="site-import"
    ),
    re_path(
        r"^import-content/$",
        admin_views.MainImportView.as_view(),
        name="main-import"
    ),
    re_path(
        r"^choose-article-parent/$",
        admin_views.ArticleChooserView.as_view(
            model_admin=admin_views.ArticleModelAdmin()
        ), name="article-parent-chooser"
    ),
    re_path(
        r"^import-articles/$",
        admin_views.ArticleImportView.as_view(),
        name="article-import"
    ),
    re_path(
        r"^choose-section-parent/$",
        admin_views.SectionParentChooserView.as_view(
            model_admin=admin_views.SectionModelAdmin()
        ), name="section-parent-chooser"
    ),
    re_path(
        r"^import-section/$",
        admin_views.SectionImportView.as_view(),
        name="section-import"
    ),
    re_path(
        r"^import-begun/$",
        admin_views.ImportBegun.as_view(),
        name="begun-import"
    ),
]
