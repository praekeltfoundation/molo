from django.conf.urls import url

from molo.core.content_import.api import admin_views

urlpatterns = [
    url(r'^test_link/$', admin_views.ImportView.as_view(), name='test-api-import-view'),
]