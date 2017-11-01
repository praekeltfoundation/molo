from django.conf.urls import url

from molo.core.api import admin_views

# Adding extended images endpoint to new router.
# For consistency, the "pages" and "documents"
# endpoints have also been added even though they were
# not modified.

urlpatterns = [
    url(
        r"^import-site/$",
        admin_views.SiteImportView.as_view(),
        name="site-import"
    ),
    url(
        r"^import-content/$",
        admin_views.MainImportView.as_view(),
        name="main-import"
    ),
    url(
        r"^choose-article-parent/$",
        admin_views.ArticleChooserView.as_view(
            model_admin=admin_views.ArticleModelAdmin()
        ), name="article-parent-chooser"
    ),
    url(
        r"^import-articles/$",
        admin_views.ArticleImportView.as_view(),
        name="article-import"
    ),
    url(
        r"^choose-section-parent/$",
        admin_views.SectionParentChooserView.as_view(
            model_admin=admin_views.SectionModelAdmin()
        ), name="section-parent-chooser"
    ),
    url(
        r"^import-section/$",
        admin_views.SectionImportView.as_view(),
        name="section-import"
    ),
    url(
        r"^import-begun/$",
        admin_views.ImportBegun.as_view(),
        name="begun-import"
    ),
]
