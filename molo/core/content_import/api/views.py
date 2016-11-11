"""
Views for importing content from another wagtail instance
"""
from django.views.generic import TemplateView


class ImportView(TemplateView):
    """
    Test view to see if the importing of a single article can work
    """
    template_name = "api/import.html"


def apiImport(self, request):
    return ImportView.as_view()(request)
