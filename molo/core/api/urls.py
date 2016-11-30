from django.conf.urls import url

from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2 import endpoints

from molo.core.api import admin_views
from molo.core.api.endpoints import MoloImagesAPIEndpoint

# Adding extended images endpoint to new router.
# For consistency, the "pages" and "documents"
# endpoints have also been added even though they were
# not modified.
api_router = WagtailAPIRouter("wagtailapi_v2")
api_router.register_endpoint("images", MoloImagesAPIEndpoint)
api_router.register_endpoint("pages", endpoints.PagesAPIEndpoint)
api_router.register_endpoint("documents", endpoints.DocumentsAPIEndpoint)

urlpatterns = [
    url(
        r"^import-articles/$",
        admin_views.ArticleImportView.as_view(),
        name="article-import"
    ),
    url(
        r"^parent/$",
        admin_views.ArticleChooserView.as_view(
            model_admin=admin_views.ArticleModelAdmin()
        ), name="article-parent-chooser"
    ),
    url(
        r"^import-content/$",
        admin_views.MainImportView.as_view(),
        name="main-import"
    ),
]
